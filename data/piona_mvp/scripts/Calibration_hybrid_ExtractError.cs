using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;

public class Calibration_hybrid_ExtractError : MonoBehaviour
{
    public string outputFileName = "Extract_Distance";
    public bool saveData = false;

    private Dictionary<int, List<CalibrationPoint>> calibrationData;
    private HashSet<int> agentsSpawnSkipped;
    private int lastProcessedTimeIndex = -1;
    private bool isSimulationComplete = false;

    public struct CalibrationPoint
    {
        public int timeIndex;
        public Vector3 empiricalPos;
        public Vector3 validationPos;
        public float distance2D;

        public CalibrationPoint(int timeIndex, Vector3 empPos, Vector3 valPos)
        {
            this.timeIndex = timeIndex;
            this.empiricalPos = empPos;
            this.validationPos = valPos;
            this.distance2D = Vector3.Distance(new Vector3(empPos.x, 0, empPos.z), new Vector3(valPos.x, 0, valPos.z));
        }
    }


    private void Awake()
    {
        calibrationData = new Dictionary<int, List<CalibrationPoint>>();
        agentsSpawnSkipped = new HashSet<int>();
    }

    private void FixedUpdate()
    {
        if (isSimulationComplete) return;

        var simManager = Calibration_hybrid_SimulationManager.instance;
        if (simManager == null) return;

        if (!simManager.enabled && saveData)
        {
            OnSimulationComplete();
            return;
        }

        int currentTimeIndex = Mathf.FloorToInt(simManager.frame / simManager.intervalData);

        if (currentTimeIndex != lastProcessedTimeIndex)
        {
            TrackPositions(currentTimeIndex);
            lastProcessedTimeIndex = currentTimeIndex;
        }
    }

    private void TrackPositions(int timeIndex)
    {
        Calibration_hybrid_Empirical[] empAgents = FindObjectsByType<Calibration_hybrid_Empirical>(FindObjectsSortMode.InstanceID);
        Calibration_hybrid_SFM[] valAgents = FindObjectsByType<Calibration_hybrid_SFM>(FindObjectsSortMode.InstanceID);

        Dictionary<int, Vector3> empPositions = new Dictionary<int, Vector3>();
        Dictionary<int, Vector3> valPositions = new Dictionary<int, Vector3>();

        foreach (var agent in empAgents)
        {
            if (agent != null && !agent.isFinished)
            {
                int id = GetAgentId(agent.name);
                if (id != -1) empPositions[id] = agent.transform.position;
            }
        }

        foreach (var agent in valAgents)
        {
            if (agent != null && !agent.isFinished)
            {
                int id = GetAgentId(agent.name);
                if (id != -1) valPositions[id] = agent.transform.position;
            }
        }

        foreach (var empKvp in empPositions)
        {
            int agentId = empKvp.Key;
            if (valPositions.ContainsKey(agentId))
            {
                if (!agentsSpawnSkipped.Contains(agentId))
                {
                    agentsSpawnSkipped.Add(agentId);
                    continue; // Skip first spawn point
                }

                if (!calibrationData.ContainsKey(agentId))
                    calibrationData[agentId] = new List<CalibrationPoint>();

                var point = new CalibrationPoint(timeIndex, empKvp.Value, valPositions[agentId]);
                calibrationData[agentId].Add(point);
            }
        }
    }

    private int GetAgentId(string name)
    {
        if (name.StartsWith("Agent_"))
        {
            string[] parts = name.Split('_');
            if (parts.Length >= 2 && int.TryParse(parts[1], out int id))
                return id;
        }
        return -1;
    }

    private void OnSimulationComplete()
    {
        if (isSimulationComplete) return;
        isSimulationComplete = true;

        Debug.Log("[Calibration] Complete - spawn positions excluded");
        SaveCalibrationData();
    }

    private void SaveCalibrationData()
    {
        string dir = Path.Combine(Application.streamingAssetsPath, "Data/Calibration");
        if (!Directory.Exists(dir)) Directory.CreateDirectory(dir);

        string filePath = Path.Combine(dir, $"{outputFileName}_{System.DateTime.Now:yyyyMMdd_HHmmss}.csv");

        StringBuilder csv = new StringBuilder();
        csv.AppendLine("AgentID,TimeIndex,EmpX,EmpZ,ValX,ValZ,Distance2D");

        foreach (var kvp in calibrationData)
        {
            foreach (var point in kvp.Value)
            {
                csv.AppendLine($"{kvp.Key},{point.timeIndex},{point.empiricalPos.x:F3},{point.empiricalPos.z:F3},{point.validationPos.x:F3},{point.validationPos.z:F3},{point.distance2D:F3}");
            }
        }

        try
        {
            File.WriteAllText(filePath, csv.ToString());
            Debug.Log($"[Calibration] Data saved (spawn positions excluded): {filePath}");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[Calibration] Save failed: {e.Message}");
        }
    }

    private void OnDestroy()
    {
        if (!isSimulationComplete && saveData) OnSimulationComplete();
    }
}