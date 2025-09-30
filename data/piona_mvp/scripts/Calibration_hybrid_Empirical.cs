using NUnit.Framework;
using UnityEngine;
using System.Collections.Generic;

public class Calibration_hybrid_Empirical : MonoBehaviour
{
    // frame control
    float frame;
    float interval;

    // Import Data
    int pid;
    List<Calibration_hybrid_SimulationManager.FrameData> traj;

    // Position
    int nextIdx;
    Vector3 prevPos;
    Vector3 tempPos;

    // Trajectory
    LineRenderer lr;

    // Check Simulation Status
    public bool isFinished = false;


    // Update is called once per frame
    void FixedUpdate()
    {
        if (traj == null || lr == null || isFinished) return;

        // time
        frame += Time.fixedDeltaTime;

        // update trajectory & tempPos when reached
        if (frame >= interval)
        {
            //transform.position = tempPos;
            lr.positionCount++;
            lr.SetPosition(lr.positionCount - 1, tempPos);

            // set next tempPos
            prevPos = tempPos;
            nextIdx++;

            if (nextIdx < traj.Count)
            {
                tempPos = traj[nextIdx].pos;
            }
            else
            {
                isFinished = true;
                DestroyMeshReal();

                return;
            }

            frame -= interval;
        }
        else
        {
            // move with Lerp
            float t = frame / interval;
            transform.position = Vector3.Lerp(prevPos, tempPos, t);
        }
    }


    public void InitializeReal(int pid, List<Calibration_hybrid_SimulationManager.FrameData> realTraj, float interval)
    {
        this.pid = pid;
        traj = realTraj;
        this.interval = interval;

        // spawn setting
        nextIdx = 1;
        prevPos = traj[0].pos;
        tempPos = traj.Count > 1 ? traj[1].pos : traj[0].pos;
        frame = 0f;
        isFinished = false;

        // LineRenderer setting
        lr = GetComponentInChildren<LineRenderer>();
        lr.useWorldSpace = true;
        lr.positionCount = 1;
        lr.SetPosition(0, prevPos);
    }


    public void DestroyMeshReal()
    {
        // detach LineRenderer
        lr.transform.SetParent(null, true);
        lr.gameObject.name = $"Traj_{pid}_real";

        Destroy(gameObject);
    }
}
