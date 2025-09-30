using System.Collections.Generic;
using System;
using UnityEngine;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

public class Calibration_hybrid_SimulationManager : MonoBehaviour
{
    // Instancing
    public static Calibration_hybrid_SimulationManager instance;

    [Header("Simulation(Observation) Time Control")]
    [Range(1f, 100f)] public float simulationSpeed = 100f;

    [Header("Data Setting")]
    public string csvFileName = "atc_resampled_1s_noQueing.csv";

    public Dictionary<int, List<FrameData>> tracks;
    public List<int> allPersonId;
    int maxTimeIndex;

    public int startPid = 0;
    int startTimeIndex = 0;

    [Header("Frame Interval")]
    public float frame = 0f;

    int currentIndex = -1;
    int lastIdx = -1;

    public float intervalData = 1f;

    [Header("Agent Settings")]
    public GameObject empiricalAgentPrefab;
    public GameObject validationAgentPrefab;

    Dictionary<int, Calibration_hybrid_Empirical> empiricalAgents;
    Dictionary<int, Calibration_hybrid_SFM> validationAgents;

    public struct FrameData
    {
        public int timeIndex;
        public Vector3 pos;
        public float speed;

        public FrameData(int timeIndex, Vector3 pos, float speed)
        {
            this.timeIndex = timeIndex;
            this.pos = pos;
            this.speed = speed;
        }
    }

    // Ready to Play
    bool isReady = false;


    private void Awake()
    {
        if (instance == null)
        {
            instance = this;
        }
    }


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    async void Start()
    {
        // init data structure
        tracks = new Dictionary<int, List<FrameData>>();
        allPersonId = new List<int>();

        empiricalAgents = new Dictionary<int, Calibration_hybrid_Empirical>();
        validationAgents = new Dictionary<int, Calibration_hybrid_SFM>();

        // set data path
        string filePath = Path.Combine(Application.streamingAssetsPath, $"Data/PedestrianTrajectory/ATC/{csvFileName}");
        Debug.Log($"[Validation] Loading Data from {filePath}");

        // background parsing
        await Task.Run(() => LoadCsvParallel(filePath));
        Debug.Log($"[Validation] Data(CSV) Loaded : Agents = {tracks.Count}, Max Time Index = {maxTimeIndex}");

        // set init pid & timeIndex to simulate
        if (startPid != 0 && tracks.ContainsKey(startPid))
        {
            startTimeIndex = tracks[startPid][0].timeIndex;
        }

        frame = startTimeIndex * intervalData;
        currentIndex = startTimeIndex;
        lastIdx = currentIndex - 1;

        // Ready to Play
        isReady = true;
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        // wait for Read Data
        if (!isReady) return;

        // time
        Time.timeScale = simulationSpeed;
        frame += Time.fixedDeltaTime;
        currentIndex = Mathf.Min(Mathf.FloorToInt(frame / intervalData), maxTimeIndex);

        // simulate
        for (int idx = lastIdx + 1; idx <= currentIndex; idx++)
        {
            SpawnAgent(idx);
        }

        lastIdx = currentIndex;

        if (frame >= maxTimeIndex)
        {
            Debug.Log("[Validation] Simulation Complete");

            enabled = false;
        }
    }


    void LoadCsvParallel(string path)
    {
        // read all lines(include header)
        string[] allLines = File.ReadAllLines(path);
        if (allLines.Length <= 1)
        {
            return;
        }

        // (skip header)parallel parsing with PLINQ(Parallel Language Intergrated Query)
        var parsed = allLines
            .Skip(1)
            .AsParallel()
            .WithDegreeOfParallelism(Environment.ProcessorCount)
            .Select(line =>
            {
                var tokens = line.Split(',');

                int pid = int.Parse(tokens[0]);
                int tidx = int.Parse(tokens[1]);
                float x = float.Parse(tokens[2]);
                float z = float.Parse(tokens[3]);
                float y = float.Parse(tokens[4]);
                float speed = float.Parse(tokens[5]);

                return new { pid, frame = new FrameData(tidx, new Vector3(x, 0, z), speed) };
            })
            .ToArray();

        // merge parsed data(single thread)
        maxTimeIndex = 0;
        foreach (var item in parsed)
        {
            if (!tracks.TryGetValue(item.pid, out var list))
            {
                list = new List<FrameData>();
                tracks[item.pid] = list;
                allPersonId.Add(item.pid);
            }

            list.Add(item.frame);
            maxTimeIndex = Mathf.Max(maxTimeIndex, item.frame.timeIndex);
        }

        // sort pos list by timeIndex for each ag
        foreach (var kvp in tracks)
        {
            kvp.Value.Sort((a, b) => a.timeIndex.CompareTo(b.timeIndex));
        }

        // reorder allPersonId by timeIndex(Origin t)
        allPersonId = tracks
            .OrderBy(kvp => kvp.Value[0].timeIndex)
            .ThenBy(kvp => kvp.Key)
            .Select(kvp => kvp.Key)
            .ToList();
    }


    void SpawnAgent(int timeIndex)
    {
        foreach (int pid in allPersonId)
        {
            if (empiricalAgents.ContainsKey(pid)) continue;
            if (validationAgents.ContainsKey(pid)) continue;

            var traj = tracks[pid];

            if (traj[0].timeIndex == timeIndex && !empiricalAgents.ContainsKey(pid))
            {
                // instance prefab
                var ag = Instantiate(empiricalAgentPrefab, traj[0].pos, Quaternion.identity);
                ag.name = $"Agent_{pid}_real";

                // initialize
                var comp = ag.GetComponent<Calibration_hybrid_Empirical>();

                comp.InitializeReal(pid, traj, intervalData);

                empiricalAgents[pid] = comp;
            }

            if (traj[0].timeIndex == timeIndex && !validationAgents.ContainsKey(pid))
            {
                // instance prefab
                var ag = Instantiate(validationAgentPrefab, traj[0].pos, Quaternion.identity);
                ag.name = $"Agent_{pid}_virt";

                // initialize
                var comp = ag.GetComponent<Calibration_hybrid_SFM>();

                comp.InitializeVirt(pid, traj, intervalData);

                validationAgents[pid] = comp;
            }
        }
    }
}
