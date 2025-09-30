using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using Newtonsoft.Json;

/// <summary>
/// Custom JSON converter for Unity Vector3 to avoid self-referencing loops
/// </summary>
public class Vector3JsonConverter : JsonConverter<Vector3>
{
    public override void WriteJson(JsonWriter writer, Vector3 value, JsonSerializer serializer)
    {
        writer.WriteStartObject();
        writer.WritePropertyName("x");
        writer.WriteValue(value.x);
        writer.WritePropertyName("y");
        writer.WriteValue(value.y);
        writer.WritePropertyName("z");
        writer.WriteValue(value.z);
        writer.WriteEndObject();
    }

    public override Vector3 ReadJson(JsonReader reader, Type objectType, Vector3 existingValue, bool hasExistingValue, JsonSerializer serializer)
    {
        if (reader.TokenType == JsonToken.Null)
            return Vector3.zero;

        float x = 0, y = 0, z = 0;
        
        while (reader.Read())
        {
            if (reader.TokenType == JsonToken.EndObject)
                break;
                
            if (reader.TokenType == JsonToken.PropertyName)
            {
                string propertyName = reader.Value.ToString();
                reader.Read();
                
                switch (propertyName)
                {
                    case "x":
                        x = Convert.ToSingle(reader.Value);
                        break;
                    case "y":
                        y = Convert.ToSingle(reader.Value);
                        break;
                    case "z":
                        z = Convert.ToSingle(reader.Value);
                        break;
                }
            }
        }
        
        return new Vector3(x, y, z);
    }
}

public class Calibration_ParameterInterface : MonoBehaviour
{
    public static Calibration_ParameterInterface instance;
    
    // Editor mode support - NEW
    [Header("Editor Mode Settings")]
    public static bool IsEditorMode { get; private set; } = false;
    public string InstanceId { get; private set; } = "";
    private static Dictionary<string, Calibration_ParameterInterface> editorInstances = new Dictionary<string, Calibration_ParameterInterface>();

    [Header("Communication Settings")]
    public string parameterInputPath = "StreamingAssets/Calibration/Input";
    public string resultOutputPath = "StreamingAssets/Calibration/Output";
    public string parameterFileName = "parameters.json";
    public string resultFileName = "simulation_result.json";

    [Header("Runtime Settings")]
    public bool isParameterMode = false;
    public bool autoExit = false;
    public float exitDelay = 1f;

    private ParameterSet currentParameters;
    private SimulationResult currentResult;
    public bool parametersLoaded = false;
    public bool simulationCompleted = false;
    private static bool isBatchMode = false;
    
    // Parameter bounds for optimization
    public static Dictionary<string, (float min, float max)> ParameterBounds = new Dictionary<string, (float, float)>
    {
        {"minimalDistance", (0.15f, 0.35f)},
        {"relaxationTime", (0.3f, 0.8f)},
        {"repulsionStrengthAgent", (0.8f, 1.8f)},
        {"repulsionRangeAgent", (3.0f, 7.0f)},
        {"lambdaAgent", (0.2f, 0.5f)},
        {"repulsionStrengthObs", (0.6f, 1.5f)},
        {"repulsionRangeObs", (3.0f, 7.0f)},
        {"lambdaObs", (0.2f, 0.5f)},
        {"k", (5.0f, 12.0f)},
        {"kappa", (3.0f, 7.0f)},
        {"obsK", (2.0f, 4.5f)},
        {"obsKappa", (0.0f, 2.0f)},
        {"considerationRange", (2.0f, 4.0f)},
        {"viewAngle", (120f, 180f)},
        {"viewAngleMax", (200f, 270f)},
        {"viewDistance", (3.0f, 10.0f)},
        {"rayStepAngle", (15f, 45f)},
        {"visibleFactor", (0.5f, 0.9f)}
    };

    [System.Serializable]
    public class ParameterSet
    {
        // === 18 Calibration Parameters ===
        
        // 기본 물리 파라미터 (현실성 보장)
        public float minimalDistance = 0.2f;      // [0.15, 0.35]
        public float relaxationTime = 0.5f;       // [0.3, 0.8]
        
        // 에이전트 간 상호작용 (사회적 행동 보장)
        public float repulsionStrengthAgent = 1.2f;  // [0.8, 1.8]
        public float repulsionRangeAgent = 5f;       // [3.0, 7.0]
        public float lambdaAgent = 0.35f;            // [0.2, 0.5]
        
        // 장애물 상호작용
        public float repulsionStrengthObs = 1f;      // [0.6, 1.5]
        public float repulsionRangeObs = 5f;         // [3.0, 7.0]
        public float lambdaObs = 0.35f;              // [0.2, 0.5]
        
        // 물리적 접촉력 (현실성 보장)
        public float k = 8f;                         // [5.0, 12.0]
        public float kappa = 5f;                     // [3.0, 7.0]
        public float obsK = 3f;                      // [2.0, 4.5]
        public float obsKappa = 0f;                  // [0.0, 2.0]
        
        // 인지/시야 파라미터
        public float considerationRange = 2.5f;      // [2.0, 4.0]
        public float viewAngle = 150f;               // [120, 180]
        public float viewAngleMax = 240f;            // [200, 270]
        public float viewDistance = 5f;              // [3.0, 10.0]
        public float rayStepAngle = 30f;             // [15, 45]
        public float visibleFactor = 0.7f;           // [0.5, 0.9]
        
        // === Fixed Parameters (Not calibrated) ===
        public float mass = 1f;
        public float agentRadius = 0.3f;
        public float rotationSpeed = 5f;
        
        // === Simulation Settings ===
        public int randomSeed = 42;
        public string fidelityLevel = "L3"; // L1, L2, L3
        public float agentSamplingRatio = 1.0f;
        public int maxTimeIndex = -1; // -1 means full simulation
        
        // === Metadata ===
        public string experimentId = "";
        public DateTime timestamp;
        
        // Validate parameters within bounds
        public void ValidateAndClamp()
        {
            minimalDistance = Mathf.Clamp(minimalDistance, 0.15f, 0.35f);
            relaxationTime = Mathf.Clamp(relaxationTime, 0.3f, 0.8f);
            repulsionStrengthAgent = Mathf.Clamp(repulsionStrengthAgent, 0.8f, 1.8f);
            repulsionRangeAgent = Mathf.Clamp(repulsionRangeAgent, 3.0f, 7.0f);
            lambdaAgent = Mathf.Clamp(lambdaAgent, 0.2f, 0.5f);
            repulsionStrengthObs = Mathf.Clamp(repulsionStrengthObs, 0.6f, 1.5f);
            repulsionRangeObs = Mathf.Clamp(repulsionRangeObs, 3.0f, 7.0f);
            lambdaObs = Mathf.Clamp(lambdaObs, 0.2f, 0.5f);
            k = Mathf.Clamp(k, 5.0f, 12.0f);
            kappa = Mathf.Clamp(kappa, 3.0f, 7.0f);
            obsK = Mathf.Clamp(obsK, 2.0f, 4.5f);
            obsKappa = Mathf.Clamp(obsKappa, 0.0f, 2.0f);
            considerationRange = Mathf.Clamp(considerationRange, 2.0f, 4.0f);
            viewAngle = Mathf.Clamp(viewAngle, 120f, 180f);
            viewAngleMax = Mathf.Clamp(viewAngleMax, 200f, 270f);
            viewDistance = Mathf.Clamp(viewDistance, 3.0f, 10.0f);
            rayStepAngle = Mathf.Clamp(rayStepAngle, 15f, 45f);
            visibleFactor = Mathf.Clamp(visibleFactor, 0.5f, 0.9f);
        }
    }

    [System.Serializable]
    public class SimulationResult
    {
        public string experimentId;
        public DateTime startTime;
        public DateTime endTime;
        public float executionTimeSeconds;
        
        public int totalAgents;
        public int actualAgents;
        public int maxTimeIndex;
        public int actualTimeIndex;
        
        public bool successful;
        public string errorMessage = "";
        
        public Dictionary<string, object> metrics = new Dictionary<string, object>();
        public List<AgentTrajectoryData> trajectories = new List<AgentTrajectoryData>();
        
        // Performance metrics
        public float avgFPS;
        public long memoryUsageMB;
    }

    [System.Serializable]
    public class AgentTrajectoryData
    {
        public int agentId;
        public List<TrajectoryPoint> empiricalPoints = new List<TrajectoryPoint>();
        public List<TrajectoryPoint> validationPoints = new List<TrajectoryPoint>();
    }

    [System.Serializable]
    public class TrajectoryPoint
    {
        public int timeIndex;
        public Vector3 position;
        public float speed;
        public DateTime timestamp;

        public TrajectoryPoint(int timeIndex, Vector3 position, float speed)
        {
            this.timeIndex = timeIndex;
            this.position = position;
            this.speed = speed;
            this.timestamp = DateTime.Now;
        }
    }

    private void Awake()
    {
        // Check if running in Editor mode (for parallel simulations)
        IsEditorMode = Application.isEditor;
        
        if (IsEditorMode)
        {
            // In Editor mode, use instance-based management instead of singleton
            InstanceId = gameObject.name.Replace("ParameterInterface_", "");
            
            if (!editorInstances.ContainsKey(InstanceId))
            {
                editorInstances[InstanceId] = this;
                Debug.Log($"[ParameterInterface] Instance {InstanceId} initialized");
            }
            else
            {
                Debug.LogWarning($"[ParameterInterface] Duplicate Editor mode instance: {InstanceId}");
                Destroy(gameObject);
                return;
            }
        }
        else
        {
            // Original singleton behavior for batch mode
            if (instance == null)
            {
                instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
                return;
            }
        }

        // Parse command line arguments
        ParseCommandLineArguments();
        
        // Initialize paths
        InitializePaths();
        
        // Initialize result object
        InitializeResult();
    }

    private void ParseCommandLineArguments()
    {
        string[] args = Environment.GetCommandLineArgs();
        
        for (int i = 0; i < args.Length; i++)
        {
            switch (args[i].ToLower())
            {
                case "-parametermode":
                    isParameterMode = true;
                    Debug.Log("[ParameterInterface] Parameter mode enabled");
                    break;
                    
                case "-autoexit":
                    autoExit = true;
                    Debug.Log("[ParameterInterface] Auto-exit enabled");
                    break;
                    
                case "-parameterfile":
                    if (i + 1 < args.Length)
                    {
                        parameterFileName = args[i + 1];
                        Debug.Log($"[ParameterInterface] Parameter file: {parameterFileName}");
                    }
                    break;
                    
                case "-resultfile":
                    if (i + 1 < args.Length)
                    {
                        resultFileName = args[i + 1];
                        Debug.Log($"[ParameterInterface] Result file: {resultFileName}");
                    }
                    break;
                    
                case "-seed":
                    if (i + 1 < args.Length && int.TryParse(args[i + 1], out int seed))
                    {
                        UnityEngine.Random.InitState(seed);
                        Debug.Log($"[ParameterInterface] Random seed set: {seed}");
                    }
                    break;
            }
        }
    }

    private void InitializePaths()
    {
        string inputDir = Path.Combine(Application.streamingAssetsPath, "Calibration/Input");
        string outputDir = Path.Combine(Application.streamingAssetsPath, "Calibration/Output");
        
        if (!Directory.Exists(inputDir))
        {
            Directory.CreateDirectory(inputDir);
            Debug.Log($"[ParameterInterface] Created input directory: {inputDir}");
        }
        
        if (!Directory.Exists(outputDir))
        {
            Directory.CreateDirectory(outputDir);
            Debug.Log($"[ParameterInterface] Created output directory: {outputDir}");
        }
    }

    private void InitializeResult()
    {
        currentResult = new SimulationResult
        {
            startTime = DateTime.Now,
            successful = false,
            experimentId = Guid.NewGuid().ToString()
        };
    }

    private void Start()
    {
        // Generate parameter bounds metadata for Python optimization (only once)
        SaveParameterBoundsMetadata();
        
        // In Editor mode with instance management, wait for proper initialization
        if (IsEditorMode && !string.IsNullOrEmpty(InstanceId))
        {
            // Check if this instance has been configured through InitializeForInstance
            if (isParameterMode && !string.IsNullOrEmpty(parameterFileName))
            {
                // Only load if parameters haven't been loaded yet (prevent double loading)
                if (!parametersLoaded)
                {
                    Debug.Log($"[ParameterInterface] Instance {InstanceId} - Start() loading parameters");
                    LoadParametersFromFile();
                }
                else
                {
                    Debug.Log($"[ParameterInterface] Instance {InstanceId} - Parameters already loaded, skipping");
                }
            }
            else
            {
                // Wait for InitializeForInstance to be called
                Debug.Log($"[ParameterInterface] Instance {InstanceId} - Waiting for initialization...");
                StartCoroutine(WaitForInstanceInitialization());
            }
        }
        else if (isParameterMode)
        {
            LoadParametersFromFile();
        }
        else
        {
            // Use default parameters
            currentParameters = new ParameterSet();
            parametersLoaded = true;
            Debug.Log("[ParameterInterface] Using default parameters");
            LogParameterValues();
        }
    }
    
    /// <summary>
    /// Coroutine to wait for InitializeForInstance to be called in Editor mode
    /// </summary>
    private IEnumerator WaitForInstanceInitialization()
    {
        Debug.Log($"[ParameterInterface] Instance {InstanceId} waiting for initialization...");
        
        float waitTime = 0f;
        const float maxWaitTime = 5f;
        
        while (!isParameterMode && waitTime < maxWaitTime)
        {
            yield return new WaitForSeconds(0.1f);
            waitTime += 0.1f;
        }
        
        if (isParameterMode && !string.IsNullOrEmpty(parameterFileName))
        {
            Debug.Log($"[ParameterInterface] Instance {InstanceId} initialized, loading parameters...");
            LoadParametersFromFile();
        }
        else
        {
            Debug.LogWarning($"[ParameterInterface] Instance {InstanceId} initialization timeout, using defaults");
            currentParameters = new ParameterSet();
            parametersLoaded = true;
            LogParameterValues();
        }
    }

    public void LoadParametersFromFile()
    {
        Debug.Log($"[ParameterInterface] *** LoadParametersFromFile() CALLED for Instance {InstanceId} ***");
        Debug.Log($"[ParameterInterface] Instance {InstanceId} - isParameterMode: {isParameterMode}");
        Debug.Log($"[ParameterInterface] Instance {InstanceId} - parameterFileName: '{parameterFileName}'");
        
        // Ensure currentResult is initialized before proceeding
        if (currentResult == null)
        {
            Debug.Log($"[ParameterInterface] Instance {InstanceId} - currentResult is null, initializing...");
            InitializeResult();
        }
        
        string inputDir = Path.Combine(Application.streamingAssetsPath, "Calibration/Input");
        string fullPath = Path.Combine(inputDir, parameterFileName);
        
        Debug.Log($"[ParameterInterface] Instance {InstanceId} - StreamingAssetsPath: {Application.streamingAssetsPath}");
        Debug.Log($"[ParameterInterface] Instance {InstanceId} - Full path: {fullPath}");
        Debug.Log($"[ParameterInterface] Instance {InstanceId} - Directory exists: {Directory.Exists(inputDir)}");
        
        try
        {
            // First try the specific filename
            if (File.Exists(fullPath))
            {
                Debug.Log($"[ParameterInterface] Instance {InstanceId} - Found specific parameter file, loading...");
                LoadParameterFile(fullPath);
            }
            // If not found, look for the latest parameter file
            else
            {
                Debug.LogWarning($"[ParameterInterface] Instance {InstanceId} - Specific file not found: {fullPath}");
                
                // List all files in directory for debugging
                if (Directory.Exists(inputDir))
                {
                    var allFiles = Directory.GetFiles(inputDir, "*.json");
                    Debug.Log($"[ParameterInterface] Instance {InstanceId} - Available JSON files in directory: {string.Join(", ", allFiles.Select(Path.GetFileName))}");
                }
                
                string foundFile = FindLatestParameterFile(inputDir);
                if (!string.IsNullOrEmpty(foundFile))
                {
                    Debug.Log($"[ParameterInterface] Instance {InstanceId} - Using latest parameter file: {foundFile}");
                    LoadParameterFile(foundFile);
                }
                else
                {
                    Debug.LogError($"[ParameterInterface] Instance {InstanceId} - No parameter files found in: {inputDir}");
                    currentResult.errorMessage = $"No parameter files found in: {inputDir}";
                    SaveResultToFile();
                    
                    if (autoExit)
                    {
                        ExitApplication();
                    }
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[ParameterInterface] Instance {InstanceId} - Failed to load parameters: {e.Message}");
            Debug.LogError($"[ParameterInterface] Instance {InstanceId} - Exception details: {e.StackTrace}");
            currentResult.errorMessage = $"Failed to load parameters: {e.Message}";
            SaveResultToFile();
            
            if (autoExit)
            {
                ExitApplication();
            }
        }
    }

    private string FindLatestParameterFile(string inputDir)
    {
        try
        {
            if (!Directory.Exists(inputDir))
                return null;
                
            var parameterFiles = Directory.GetFiles(inputDir, "*_parameters.json")
                .Where(f => !f.Contains(".meta"))
                .ToArray();
            
            if (parameterFiles.Length == 0)
                return null;
                
            // Get the most recently modified file
            return parameterFiles
                .OrderByDescending(f => File.GetLastWriteTime(f))
                .FirstOrDefault();
        }
        catch (Exception e)
        {
            Debug.LogError($"[ParameterInterface] Error finding parameter files: {e.Message}");
            return null;
        }
    }
    
    private void LoadParameterFile(string filePath)
    {
        string jsonContent = File.ReadAllText(filePath);
        
        currentParameters = JsonConvert.DeserializeObject<ParameterSet>(jsonContent, GetJsonSettings());
        
        // Validate and clamp parameters within bounds
        currentParameters.ValidateAndClamp();
        
        if (!string.IsNullOrEmpty(currentParameters.experimentId))
        {
            currentResult.experimentId = currentParameters.experimentId;
        }
        
        parametersLoaded = true;
        Debug.Log($"[ParameterInterface] Parameters loaded successfully from: {filePath}");
        Debug.Log($"[ParameterInterface] Experiment ID: {currentResult.experimentId}");
        LogParameterValues();
    }

    public ParameterSet GetCurrentParameters()
    {
        return currentParameters;
    }

    public bool IsParametersLoaded()
    {
        return parametersLoaded;
    }

    public void AddTrajectoryData(int agentId, List<TrajectoryPoint> empirical, List<TrajectoryPoint> validation)
    {
        // Check if trajectory for this agent already exists
        var existingTrajectory = currentResult.trajectories.FirstOrDefault(t => t.agentId == agentId);
        
        if (existingTrajectory != null)
        {
            // Merge data into existing trajectory
            if (empirical != null && empirical.Count > 0)
            {
                existingTrajectory.empiricalPoints = new List<TrajectoryPoint>(empirical);
            }
            if (validation != null && validation.Count > 0)
            {
                existingTrajectory.validationPoints = new List<TrajectoryPoint>(validation);
            }
        }
        else
        {
            // Create new trajectory data
            var trajectoryData = new AgentTrajectoryData
            {
                agentId = agentId,
                empiricalPoints = new List<TrajectoryPoint>(empirical ?? new List<TrajectoryPoint>()),
                validationPoints = new List<TrajectoryPoint>(validation ?? new List<TrajectoryPoint>())
            };
            
            currentResult.trajectories.Add(trajectoryData);
        }
    }

    public void UpdateMetrics(string key, object value)
    {
        currentResult.metrics[key] = value;
    }

    public void OnSimulationComplete()
    {
        if (simulationCompleted) return;
        
        simulationCompleted = true;
        currentResult.endTime = DateTime.Now;
        currentResult.executionTimeSeconds = (float)(currentResult.endTime - currentResult.startTime).TotalSeconds;
        
        // Collect simulation data from SimulationManager
        CollectSimulationData();
        
        currentResult.successful = string.IsNullOrEmpty(currentResult.errorMessage);
        
        // Collect system performance metrics
        currentResult.avgFPS = 1.0f / Time.smoothDeltaTime;
        currentResult.memoryUsageMB = System.GC.GetTotalMemory(false) / 1024 / 1024;
        
        Debug.Log($"[ParameterInterface] Simulation completed. Duration: {currentResult.executionTimeSeconds:F2}s, Agents: {currentResult.actualAgents}, TimeIndex: {currentResult.actualTimeIndex}");
        
        SaveResultToFile();
        
        // In batch mode, the BatchModeController handles Unity exit
        // Don't use autoExit to avoid conflicts
        if (autoExit && !isBatchMode)
        {
            Invoke(nameof(ExitApplication), exitDelay);
        }
    }
    
    private void CollectSimulationData()
    {
        try
        {
            // Get SimulationManager instance
            var simManager = Calibration_SimulationManager.GetInstance(InstanceId);
            if (simManager != null)
            {
                // Collect basic simulation metrics
                currentResult.totalAgents = simManager.allPersonId?.Count ?? 0;
                currentResult.actualAgents = (simManager.empiricalAgents?.Count ?? 0) + (simManager.validationAgents?.Count ?? 0);
                currentResult.maxTimeIndex = simManager.maxTimeIndex;
                currentResult.actualTimeIndex = (int)simManager.frame;
                
                // Update metrics with correct actual agent count
                UpdateMetrics("actualAgents", currentResult.actualAgents);
                
                Debug.Log($"[ParameterInterface] Collected simulation data - Total: {currentResult.totalAgents}, Active: {currentResult.actualAgents}, MaxTime: {currentResult.maxTimeIndex}, ActualTime: {currentResult.actualTimeIndex}");
            }
            else
            {
                Debug.LogWarning($"[ParameterInterface] Instance {InstanceId} - SimulationManager not found for data collection");
                
                // Set default values if SimulationManager is not available
                currentResult.totalAgents = 0;
                currentResult.actualAgents = 0;
                currentResult.maxTimeIndex = 0;
                currentResult.actualTimeIndex = 0;
            }
            
            // Note: trajectories collection should be handled by agents themselves
            // via AddAgentTrajectory() calls during simulation
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[ParameterInterface] Instance {InstanceId} - Error collecting simulation data: {e.Message}");
            currentResult.errorMessage = $"Data collection error: {e.Message}";
        }
    }

    private void SaveResultToFile()
    {
        // Ensure currentResult is initialized
        if (currentResult == null)
        {
            Debug.LogWarning($"[ParameterInterface] Instance {InstanceId} - currentResult is null, cannot save result file");
            return;
        }
        
        // Use resultFileName as-is since it's already unique per instance
        string fullPath = Path.Combine(Application.streamingAssetsPath, "Calibration/Output", resultFileName);
        
        try
        {
            
            // Configure JSON serialization settings to handle Vector3 and prevent circular references
            string jsonContent = JsonConvert.SerializeObject(currentResult, GetJsonSettings());
            File.WriteAllText(fullPath, jsonContent);
            
            Debug.Log($"[ParameterInterface] Results saved to: {fullPath}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[ParameterInterface] Failed to save results: {e.Message}");
        }
    }

    private void ExitApplication()
    {
        Debug.Log("[ParameterInterface] Exiting application...");
        
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }

    private void OnDestroy()
    {
        if (!simulationCompleted && currentResult != null)
        {
            currentResult.errorMessage = "Application terminated before completion";
            SaveResultToFile();
        }
    }

    // Public API for external scripts
    public static bool IsReady()
    {
        return instance != null && instance.parametersLoaded;
    }

    public static ParameterSet GetParameters()
    {
        return instance?.currentParameters;
    }

    public static void NotifySimulationComplete()
    {
        instance?.OnSimulationComplete();
    }

    public static void AddAgentTrajectory(int agentId, List<TrajectoryPoint> empirical, List<TrajectoryPoint> validation)
    {
        instance?.AddTrajectoryData(agentId, empirical, validation);
    }

    public static void SetMetric(string key, object value)
    {
        instance?.UpdateMetrics(key, value);
    }

    /// <summary>
    /// Get configured JSON settings for safe Vector3 serialization
    /// </summary>
    private static JsonSerializerSettings GetJsonSettings()
    {
        return new JsonSerializerSettings
        {
            Formatting = Formatting.Indented,
            ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
            Converters = { new Vector3JsonConverter() }
        };
    }

    private void LogParameterValues()
    {
        if (currentParameters == null) return;
        
        // Only log essential parameter information
        Debug.Log($"[ParameterInterface] Parameters loaded for experiment: {currentParameters.experimentId}");
    }

    // Generate parameter bounds metadata for Python
    public static void SaveParameterBoundsMetadata()
    {
        string outputDir = Path.Combine(Application.streamingAssetsPath, "Calibration/Output");
        if (!Directory.Exists(outputDir))
        {
            Directory.CreateDirectory(outputDir);
        }
        
        var boundsData = new Dictionary<string, object>
        {
            {"parameter_count", 18},
            {"bounds", ParameterBounds},
            {"parameter_names", new List<string>(ParameterBounds.Keys)},
            {"created_at", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")}
        };
        
        string filePath = Path.Combine(outputDir, "parameter_bounds.json");
        
        try
        {
            // Use same JSON settings for consistency
            string jsonContent = JsonConvert.SerializeObject(boundsData, GetJsonSettings());
            File.WriteAllText(filePath, jsonContent);
            Debug.Log($"[ParameterInterface] Parameter bounds metadata saved to: {filePath}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[ParameterInterface] Failed to save parameter bounds: {e.Message}");
        }
    }
    
    // ===== EDITOR MODE SUPPORT METHODS - NEW =====
    
    /// <summary>
    /// Set Editor mode for parallel simulation support
    /// </summary>
    public static void SetEditorMode(bool editorMode)
    {
        IsEditorMode = editorMode;
        Debug.Log($"[ParameterInterface] Editor mode set to: {editorMode}");
    }
    
    /// <summary>
    /// Initialize a specific instance for Editor mode parallel execution
    /// </summary>
    public void InitializeForInstance(string instanceId, string parameterFile, string resultFile)
    {
        InstanceId = instanceId;
        parameterFileName = parameterFile;
        resultFileName = resultFile;
        isParameterMode = true;
        autoExit = false; // Managed by CalibrationBatchRunner
        
        Debug.Log($"[ParameterInterface] Instance {instanceId} initialized with files: {parameterFile} -> {resultFile}");
        Debug.Log($"[ParameterInterface] Instance {instanceId} - isParameterMode: {isParameterMode}, parameterFileName: {parameterFileName}");
        
        // Ensure currentResult is initialized before loading parameters
        if (currentResult == null)
        {
            Debug.Log($"[ParameterInterface] Instance {instanceId} - Initializing result object...");
            InitializeResult();
        }
        
        // Initialize paths to ensure directories exist
        InitializePaths();
        
        // ALWAYS load parameters immediately in Editor mode, regardless of Start() timing
        Debug.Log($"[ParameterInterface] Loading parameters immediately for instance {instanceId}");
        LoadParametersFromFile();
    }
    
    /// <summary>
    /// Get specific instance by ID for Editor mode
    /// </summary>
    public static Calibration_ParameterInterface GetInstance(string instanceId)
    {
        if (IsEditorMode && editorInstances.ContainsKey(instanceId))
        {
            return editorInstances[instanceId];
        }
        return instance; // Fallback to singleton for batch mode
    }
    
    /// <summary>
    /// Check if specific instance is ready (parameters loaded)
    /// </summary>
    public static bool IsInstanceReady(string instanceId)
    {
        var inst = GetInstance(instanceId);
        return inst != null && inst.parametersLoaded;
    }
    
    /// <summary>
    /// Check if specific instance has completed simulation
    /// </summary>
    public static bool IsInstanceCompleted(string instanceId)
    {
        var inst = GetInstance(instanceId);
        return inst != null && inst.simulationCompleted;
    }
    
    /// <summary>
    /// Get all active Editor mode instances
    /// </summary>
    public static List<string> GetActiveInstances()
    {
        return new List<string>(editorInstances.Keys);
    }
    
    /// <summary>
    /// Clean up Editor mode instance
    /// </summary>
    public static void CleanupInstance(string instanceId)
    {
        if (IsEditorMode && editorInstances.ContainsKey(instanceId))
        {
            editorInstances.Remove(instanceId);
            Debug.Log($"[ParameterInterface] Instance {instanceId} cleaned up");
        }
    }
    
    /// <summary>
    /// Clean up all Editor mode instances
    /// </summary>
    public static void CleanupAllInstances()
    {
        editorInstances.Clear();
        Debug.Log("[ParameterInterface] All Editor mode instances cleaned up");
    }
    
    /// <summary>
    /// Force set Editor mode and InstanceId for CalibrationBatchRunner
    /// </summary>
    public void ForceEditorModeSetup(string instanceId)
    {
        IsEditorMode = true;
        InstanceId = instanceId;
        
        if (!editorInstances.ContainsKey(InstanceId))
        {
            editorInstances[InstanceId] = this;
        }
        
        Debug.Log($"[ParameterInterface] Editor mode forced for instance: {InstanceId}");
    }

#if UNITY_EDITOR
    /// <summary>
    /// Legacy batch mode execution (kept for compatibility)
    /// Use "Run Parallel Simulations" instead for better performance
    /// </summary>
    [UnityEditor.MenuItem("Calibration/Legacy - Run Single Simulation")]
    public static void RunBatchModeSimulation()
    {
        ExecuteBatchModeSimulation();
    }
#endif

    /// <summary>
    /// Static method to execute calibration simulation in batch mode
    /// Called by Python via -executeMethod command line argument
    /// </summary>
    public static void ExecuteBatchModeSimulation()
    {
        Debug.Log("[ParameterInterface] Starting batch mode calibration simulation...");

        // Load the Calibration scene
#if UNITY_EDITOR
        string calibrationScenePath = "Assets/VeryOld_P01_s/Scene/PedModel/Calibration.unity";
        UnityEditor.SceneManagement.EditorSceneManager.OpenScene(calibrationScenePath);
        Debug.Log($"[ParameterInterface] Loaded Calibration scene: {calibrationScenePath}");
#else
        // In batch mode, use SceneManager to load scene by name
        // Note: The scene must be added to Build Settings for this to work
        string sceneName = "Calibration";
        SceneManager.LoadScene(sceneName);
        Debug.Log($"[ParameterInterface] Loaded Calibration scene: {sceneName}");
#endif

        // Set batch mode flag to ensure proper exit handling
        isBatchMode = true;
        
        // Create a GameObject to handle the batch mode monitoring
        GameObject batchController = new GameObject("BatchModeController");
        BatchModeController controller = batchController.AddComponent<BatchModeController>();
        controller.StartMonitoring();
        
        Debug.Log("[ParameterInterface] Batch mode controller created and monitoring started.");
    }
}

/// <summary>
/// Helper MonoBehaviour to monitor batch mode simulation completion
/// </summary>
public class BatchModeController : MonoBehaviour
{
    public void StartMonitoring()
    {
        // DontDestroyOnLoad is not needed in batch mode as there are no scene transitions
        // and it's not supported in Unity Editor mode
        StartCoroutine(MonitorSimulationCompletion());
    }
    
    private IEnumerator MonitorSimulationCompletion()
    {
        Debug.Log("[BatchModeController] Waiting for simulation to complete...");
        
        // Wait until ParameterInterface instance is created and simulation starts
        while (Calibration_ParameterInterface.instance == null)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        // Wait for parameters to be loaded
        while (!Calibration_ParameterInterface.instance.parametersLoaded)
        {
            yield return new WaitForSeconds(0.1f);
        }
        
        Debug.Log("[BatchModeController] Parameters loaded, simulation starting...");
        
        // Wait for simulation to complete
        while (!Calibration_ParameterInterface.instance.simulationCompleted)
        {
            yield return new WaitForSeconds(0.5f);
        }
        
        Debug.Log("[BatchModeController] Simulation completed, exiting Unity...");
        
        // Give a small delay to ensure all file operations are complete
        yield return new WaitForSeconds(2.0f);
        
        // Exit Unity
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }
}