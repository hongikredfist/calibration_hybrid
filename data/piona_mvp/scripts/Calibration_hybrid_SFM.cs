using System.Collections.Generic;
using UnityEngine;
using UnityEngine.TextCore;

public class Calibration_hybrid_SFM : MonoBehaviour
{
    // frame control
    float frame;
    float interval;
    float frameVisibility = 0f;
    public float intervalVisibility = 0.1f;

    Vector3 cacheVisibility = Vector3.zero;

    // Import Data
    int pid;
    List<Calibration_hybrid_SimulationManager.FrameData> traj;

    // Mask
    [SerializeField]
    LayerMask considerMask;
    [SerializeField]
    LayerMask visibleMask;

    // Agent List
    public List<Calibration_hybrid_SFM> allAgents = new List<Calibration_hybrid_SFM>();

    // Agent Basic Info
    public float agentRadius = 0.3f;
    public float agentScale = 0.85f;
    public float minimalDistance = 0.2f;
    public float rotationSpeed = 5f;

    // Agent Driving Force
    Vector3 currentVelocity = Vector3.zero;
    Vector3 realVelocity = Vector3.zero;
    public float mass = 1f;
    public float desiredSpeed;
    public float relaxationTime = 0.5f;

    float speed;

    // Agent Repulsive Force
    public float repulsionStrengthAgent = 1.2f;
    public float repulsionRangeAgent = 5f;
    public float lambdaAgent = 0.35f;

    public float repulsionStrengthObs = 1f;
    public float repulsionRangeObs = 5f;
    public float lambdaObs = 0.35f;

    public float k = 8f;
    public float kappa = 5f;

    // Obstacle Repulsive Force
    public float obsBuffer = 0.5f;
    public float obsK = 3f;
    public float obsKappa = 0f;

    // Consideration Objects
    static Collider[] _globalNeighborBuffer;
    public int maxNeighbors = 100;
    public List<Calibration_hybrid_SFM> _neighborAgent = new List<Calibration_hybrid_SFM>();
    public List<Collider> _neighborObs = new List<Collider>();
    public float considerationRange = 2.5f;

    // Visibility
    public float viewAngle = 150f;
    public float viewAngleMax = 240f;
    public float viewDistance = 5f;
    public float rayStepAngle = 30f;
    int rayCount;
    int rayCountMax;
    int rayCountDefault;
    int maxRays;
    public float visibleFactor = 0.7f;

    // Consideration Area
    Vector3 considerPos;
    float considerRange;

    // Position
    int nextIdx;
    Vector3 prevPos;
    Vector3 tempPos;

    // Trajectory
    LineRenderer lr;

    // Check Simulation Status
    public bool isFinished = false;

    struct RayInfo
    {
        public Vector3 origin;
        public Vector3 dir;
        public float dist;
        public RayInfo(Vector3 o, Vector3 d, float di)
        {
            origin = o;
            dir = d;
            dist = di;
        }
    }
    List<RayInfo> rayBuffer;


    private void Awake()
    {
        if (_globalNeighborBuffer == null)
        {
            _globalNeighborBuffer = new Collider[maxNeighbors];
        }
    }


    private void OnEnable()
    {
        allAgents.Add(this);
    }


    private void OnDisable()
    {
        allAgents.Remove(this);
    }


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        // set speed
        speed = desiredSpeed;

        // set Ray
        float halfAngle = viewAngle * 0.5f;
        float halfAngleMax = viewAngleMax * 0.5f;

        rayCount = (int)(halfAngle / rayStepAngle);
        rayCountDefault = rayCount;
        rayCountMax = (int)(halfAngleMax / rayStepAngle);
        maxRays = 1 + (rayCount * 2);

        cacheVisibility = ComputeVisibility();
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        if (traj == null || lr == null || isFinished) return;

        // time
        frame += Time.fixedDeltaTime;
        frameVisibility += Time.fixedDeltaTime;

        // XZ Plane Movement
        Vector3 pos = transform.position;
        pos.y = 0f;
        transform.position = pos;

        // Flexible Factor
        float speedFactor = speed / desiredSpeed;
        float flexibleFactorDriving = 2f - speedFactor;

        // Search Consideration Objects
        _neighborAgent.Clear();
        _neighborObs.Clear();

        Vector3 flexibleConsiderationPos = transform.position + (currentVelocity.normalized * Mathf.Min(considerationRange, considerationRange * speedFactor));
        float flexibleConsiderationRange = Mathf.Max((agentRadius + minimalDistance + obsBuffer), Mathf.Min(considerationRange + agentRadius + minimalDistance, considerationRange * speedFactor + agentRadius + minimalDistance));

        considerPos = flexibleConsiderationPos;
        considerRange = flexibleConsiderationRange;

        int countObj = Physics.OverlapSphereNonAlloc(
            considerPos,
            considerRange,
            _globalNeighborBuffer,
            considerMask,
            QueryTriggerInteraction.Ignore
            );

        for (int i = 0; i < countObj; i++)
        {
            Collider col = _globalNeighborBuffer[i];
            int layerIndex = col.gameObject.layer;
            string layerName = LayerMask.LayerToName(layerIndex);

            Calibration_hybrid_SFM agent = col.GetComponent<Calibration_hybrid_SFM>();

            if ((agent != null) && (agent != this))
            {
                _neighborAgent.Add(agent);

                continue;
            }
            else if (layerName == "Obstacle")
            {
                _neighborObs.Add(col);
            }
        }

        // Compute Visibility
        if (frameVisibility >= intervalVisibility)
        {
            cacheVisibility = ComputeVisibility();
        }

        // Compute SFM
        Vector3 drivingForce = ComputeDrivingForce(cacheVisibility, flexibleFactorDriving);
        Vector3 repulsiveForceAgent = ComputeRepulsiveForceAgent(_neighborAgent, speedFactor);
        Vector3 repulsiveForceObs = ComputeRepulsiveForceObs(_neighborObs);
        Vector3 totalForce = drivingForce + repulsiveForceAgent + repulsiveForceObs;

        // Update Agent Transform with Euler Integration
        Vector3 acc = totalForce / mass;

        currentVelocity += acc * Time.fixedDeltaTime;
        currentVelocity.y = 0f;
        transform.position += currentVelocity * Time.fixedDeltaTime;

        // Correct Current Velocity from MTV
        Vector3 normalPos = transform.position;

        // Compute MTV
        CorrectCollisionAgent(_neighborAgent);
        CorrectCollisionObs(_neighborObs);

        if (normalPos != transform.position)
        {
            realVelocity = (transform.position - pos);

            currentVelocity -= realVelocity;
        }

        // Clamp Current Velocity by Desired Speed
        if (currentVelocity.magnitude > 4)
        {
            currentVelocity = currentVelocity.normalized * desiredSpeed;
        }

        // Update Agent Speed
        speed = currentVelocity.magnitude;

        // Update Agent Direction Angle
        Quaternion rotation = Quaternion.LookRotation(currentVelocity.normalized, Vector3.up);
        transform.rotation = Quaternion.Slerp(transform.rotation, rotation, Time.fixedDeltaTime * rotationSpeed);

        // update trajectory & tempPos when reached
        if (frame >= interval)
        {
            lr.positionCount++;
            lr.SetPosition(lr.positionCount - 1, transform.position);

            // set next tempPos
            prevPos = tempPos;
            nextIdx++;

            if (nextIdx < traj.Count)
            {
                tempPos = traj[nextIdx].pos;
                desiredSpeed = (traj[nextIdx].speed == 0f) ? 0.1f : traj[nextIdx].speed;
            }
            else
            {
                isFinished = true;
                DestroyMeshVirt();

                return;
            }

            frame -= interval;
        }

        // internal frame clear
        frameVisibility = (frameVisibility >= intervalVisibility) ? 0f : frameVisibility;
    }


    public void InitializeVirt(int pid, List<Calibration_hybrid_SimulationManager.FrameData> realTraj, float interval)
    {
        this.pid = pid;
        traj = realTraj;
        this.interval = interval;

        // spawn setting
        nextIdx = 1;
        prevPos = traj[0].pos;
        tempPos = traj.Count > 1 ? traj[1].pos : traj[0].pos;
        desiredSpeed = (traj[0].speed == 0) ? 0.1f : traj[0].speed;

        frame = 0f;
        isFinished = false;

        // LineRenderer setting
        lr = GetComponentInChildren<LineRenderer>();
        lr.useWorldSpace = true;
        lr.positionCount = 1;
        lr.SetPosition(0, prevPos);
    }


    public void DestroyMeshVirt()
    {
        // detach LineRenderer
        lr.transform.SetParent(null, true);
        lr.gameObject.name = $"Traj_{pid}_virt";

        Destroy(gameObject);
    }


    Vector3 ComputeDrivingForce(Vector3 cacheBestDir, float scaleFactor)
    {
        Vector3 tempDir = (cacheBestDir.sqrMagnitude > 0.001f) ? cacheBestDir.normalized : Vector3.zero;

        Vector3 desiredVelocity = tempDir * desiredSpeed;
        Vector3 drivingForce = mass * ((desiredVelocity - currentVelocity) / relaxationTime) * scaleFactor;

        return drivingForce;
    }


    Vector3 ComputeRepulsiveForceAgent(List<Calibration_hybrid_SFM> agents, float scaleFactor)
    {
        Vector3 totalRepulsiveForceAgent = Vector3.zero;
        Vector3 desiredDrvingDir = currentVelocity.sqrMagnitude > 0.001 ? currentVelocity.normalized : Vector3.zero;
        Vector3 drivingVelocity = currentVelocity;

        foreach (Calibration_hybrid_SFM other in agents)
        {
            if (other == this)
            {
                continue;
            }

            Vector3 diff = transform.position - other.transform.position;
            diff.y = 0f;
            float distance = diff.magnitude;
            float distanceMinBetween = (agentRadius + other.agentRadius) + minimalDistance;
            Vector3 normalBetween = diff.normalized;
            Vector3 tangent = drivingVelocity - Vector3.Dot(drivingVelocity, normalBetween) * normalBetween;

            if ((distance > distanceMinBetween) && (distance < repulsionRangeAgent))
            {
                Vector3 repulsiveSocialForce = Vector3.zero;
                float cosPhi = Vector3.Dot(desiredDrvingDir, normalBetween);
                float anistropicFactor = lambdaAgent + (1 - lambdaAgent) * ((1 + cosPhi) / 2);

                repulsiveSocialForce += repulsionStrengthAgent * Mathf.Exp((distanceMinBetween - distance) / repulsionRangeAgent) * anistropicFactor * normalBetween;

                totalRepulsiveForceAgent += repulsiveSocialForce * scaleFactor;
            }
            else if (distance <= distanceMinBetween)
            {
                Vector3 repulsiveBodyForce = Vector3.zero;
                Vector3 repulsiveFrictionForce = Vector3.zero;
                float penetration = distanceMinBetween - distance;

                tangent = (tangent.sqrMagnitude > 0.001f) ? tangent.normalized : Vector3.zero;

                repulsiveBodyForce += k * penetration * normalBetween;
                repulsiveFrictionForce += kappa * penetration * Vector3.Dot((other.currentVelocity - drivingVelocity), tangent) * tangent;

                totalRepulsiveForceAgent += (repulsiveBodyForce + repulsiveFrictionForce) * scaleFactor;
            }
        }

        return totalRepulsiveForceAgent;
    }


    Vector3 ComputeRepulsiveForceObs(List<Collider> obs)
    {
        Vector3 totalRepulsiveForceObs = Vector3.zero;
        Vector3 desiredDrvingDir = currentVelocity.sqrMagnitude > 0.001 ? currentVelocity.normalized : Vector3.zero;
        Vector3 drivingVelocity = currentVelocity;

        foreach (Collider col in obs)
        {
            Vector3 closest = col.ClosestPoint(transform.position);
            Vector3 diffObs = transform.position - closest;
            diffObs.y = 0f;

            float distance = diffObs.magnitude;
            float distanceMinBetween = (agentRadius + obsBuffer) + minimalDistance;
            Vector3 normalBetween = diffObs.normalized;
            Vector3 tangent = drivingVelocity - Vector3.Dot(drivingVelocity, normalBetween) * normalBetween;

            if ((distance > distanceMinBetween) && (distance < repulsionRangeObs))
            {
                Vector3 repulsiveSocialForce = Vector3.zero;
                float cosPhi = Vector3.Dot(desiredDrvingDir, normalBetween);
                float anistropicFactor = lambdaObs + (1 - lambdaObs) * ((1 + cosPhi) / 2);

                repulsiveSocialForce += repulsionStrengthObs * Mathf.Exp((distanceMinBetween - distance) / repulsionRangeObs) * anistropicFactor * normalBetween;

                totalRepulsiveForceObs += repulsiveSocialForce;
            }
            else if (distance <= distanceMinBetween)
            {
                Vector3 repulsiveBodyForce = Vector3.zero;
                Vector3 repulsiveFrictionForce = Vector3.zero;
                float penetration = distanceMinBetween - distance;

                tangent = (tangent.sqrMagnitude > 0.001f) ? tangent.normalized : Vector3.zero;

                repulsiveBodyForce += obsK * penetration * normalBetween;
                repulsiveFrictionForce += obsKappa * penetration * Vector3.Dot((Vector3.zero - drivingVelocity), tangent) * tangent;

                totalRepulsiveForceObs += repulsiveBodyForce + repulsiveFrictionForce;
            }
        }

        return totalRepulsiveForceObs;
    }


    void CorrectCollisionAgent(List<Calibration_hybrid_SFM> agents)
    {
        foreach (Calibration_hybrid_SFM other in agents)
        {
            if (other == this)
            {
                continue;
            }

            Vector3 diff = transform.position - other.transform.position;
            diff.y = 0;
            float distance = diff.magnitude;
            float penetrationDepth = (agentRadius + other.agentRadius) - distance;

            if (penetrationDepth > 0)
            {
                Vector3 collisionNormal = diff.normalized;
                Vector3 mtv = collisionNormal * penetrationDepth;

                transform.position += mtv / 2f;
                other.transform.position -= mtv / 2f;
            }
        }
    }


    void CorrectCollisionObs(List<Collider> obs)
    {
        CapsuleCollider agentCol = GetComponent<CapsuleCollider>();
        agentCol.radius = agentRadius;
        agentCol.height = 2 * agentScale;

        foreach (Collider col in obs)
        {
            Vector3 mtvDir;
            float mtvDist;

            bool isOverlapping = Physics.ComputePenetration(
                agentCol,
                transform.position,
                transform.rotation,
                col,
                col.transform.position,
                col.transform.rotation,
                out mtvDir,
                out mtvDist
                );

            if (isOverlapping && (mtvDist > 0))
            {
                transform.position += mtvDir * mtvDist;
            }
        }
    }


    float CastRay(Vector3 pos, Vector3 dir, float scaleFactor)
    {
        RaycastHit hit;

        if (Physics.Raycast(pos, dir, out hit, viewDistance * scaleFactor, visibleMask, QueryTriggerInteraction.Ignore))
        {
            return hit.distance;
        }

        return viewDistance * scaleFactor;
    }


    Vector3 ComputeVisibility()
    {
        Vector3 targetDiff = tempPos - transform.position;
        Vector3 tempDiff = targetDiff.normalized + (currentVelocity.normalized * visibleFactor);
        tempDiff.y = 0;

        if (tempDiff.sqrMagnitude < 0.001f)
        {
            tempDiff = transform.forward;
        }
        else
        {
            tempDiff.Normalize();
        }

        rayBuffer = new List<RayInfo>(maxRays);

        Vector3 bestDir = tempDiff;

        Vector3 radiusBufferPos01 = Quaternion.Euler(0f, 90f, 0f) * tempDiff * (agentRadius - 0.01f);
        Vector3 radiusBufferPos02 = Quaternion.Euler(0f, 90f, 0f) * tempDiff * (agentRadius + obsBuffer - 0.01f);
        Vector3 shoulderPos01 = transform.position + radiusBufferPos01;
        Vector3 shoulderPos02 = transform.position + radiusBufferPos02;
        Vector3 shoulderPos03 = transform.position - radiusBufferPos01;
        Vector3 shoulderPos04 = transform.position - radiusBufferPos02;

        float forwardDistC = CastRay(transform.position, bestDir, 1f);
        float forwardDistR01 = CastRay(shoulderPos01, bestDir, 1f);
        float forwardDistR02 = CastRay(shoulderPos02, bestDir, 1f);
        float forwardDistL01 = CastRay(shoulderPos03, bestDir, 1f);
        float forwardDistL02 = CastRay(shoulderPos04, bestDir, 1f);

        float forwardDistR = Mathf.Min(forwardDistR01, forwardDistR02);
        float forwardDistL = Mathf.Min(forwardDistL01, forwardDistL02);

        float forwardDist = Mathf.Min(forwardDistC, Mathf.Min(forwardDistR, forwardDistL));
        float bestDist = forwardDist;

        rayBuffer.Add(new RayInfo(transform.position, tempDiff, Mathf.Min(bestDist, 5f)));

        for (int i = 1; i <= rayCount; i++)
        {
            float angle = rayStepAngle * i;
            float minProp = 0.5f;
            float angleFactor = 1 + i * ((minProp - 1) / rayCount);

            Vector3 dir1 = Quaternion.Euler(0f, angle, 0f) * tempDiff;
            float dist1 = CastRay(transform.position, dir1, angleFactor);
            float w1 = Vector3.Dot(tempDiff, dir1);
            rayBuffer.Add(new RayInfo(transform.position, dir1, Mathf.Min(dist1, 5f * angleFactor)));

            Vector3 dir2 = Quaternion.Euler(0f, -angle, 0f) * tempDiff;
            float dist2 = CastRay(transform.position, dir2, angleFactor);
            float w2 = Vector3.Dot(tempDiff, dir2);
            rayBuffer.Add(new RayInfo(transform.position, dir2, Mathf.Min(dist2, 5f * angleFactor)));

            if (dist1 > bestDist || (Mathf.Approximately(dist1, bestDist) && w1 > Vector3.Dot(bestDir, targetDiff)))
            {
                bestDist = dist1;
                bestDir = dir1;
            }
            if (dist2 > bestDist || (Mathf.Approximately(dist2, bestDist) && w2 > Vector3.Dot(bestDir, targetDiff)))
            {
                bestDist = dist2;
                bestDir = dir2;
            }
        }

        if (bestDist < viewDistance * 0.1f)
        {
            rayCount = Mathf.Min(++rayCount, rayCountMax);
        }
        else
        {
            rayCount = Mathf.Max(--rayCount, rayCountDefault);
        }

        maxRays = 1 + (rayCount * 2);

        return bestDir;
    }
}
