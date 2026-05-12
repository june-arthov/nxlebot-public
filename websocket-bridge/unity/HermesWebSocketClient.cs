using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using WebSocketSharp; // Install via NuGet/Git: "WebSocket-Sharp" by sta

/// <summary>
/// Hermes WebSocket Bridge — Agent ↔ Unity controller.
/// Attach ke GameObject kosong bernama "HermesBridge" di scene.
/// </summary>
public class HermesWebSocket : MonoBehaviour
{
    [Header("Connection")]
    [SerializeField] private string serverUrl = "ws://localhost:8765";
    [SerializeField] private float reconnectDelay = 5f;

    private WebSocket _ws;
    private readonly Queue<string> _msgQueue = new Queue<string>();
    private readonly object _lock = new object();

    // Static singleton jadi agent bisa kirim command dari mana aja
    public static HermesWebSocket Instance { get; private set; }

    void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    void Start() => Connect();
    void OnDestroy() => Disconnect();

    void Update()
    {
        lock (_lock)
        {
            while (_msgQueue.Count > 0)
            {
                string raw = _msgQueue.Dequeue();
                OnMessageInternal(raw);
            }
        }
    }

    #region Core
    void Connect()
    {
        Debug.Log($"[Hermes] Connecting to {serverUrl}");
        _ws = new WebSocket(serverUrl);
        _ws.OnOpen += (s, e) =>
        {
            Debug.Log("[Hermes] Connected — sending register");
            SendJson(new { type = "register", engine = "unity", version = Application.unityVersion });
        };
        _ws.OnMessage += (s, e) =>
        {
            lock (_lock) _msgQueue.Enqueue(e.Data);
        };
        _ws.OnError += (s, e) => Debug.LogError($"[Hermes] Error: {e.Message}");
        _ws.OnClose += (s, e) =>
        {
            Debug.LogWarning($"[Hermes] Disconnected ({e.Code}). Reconnecting in {reconnectDelay}s...");
            Invoke(nameof(DoReconnect), reconnectDelay);
        };
        _ws.ConnectAsync();
    }

    void Disconnect()
    {
        if (_ws != null && _ws.IsAlive)
        {
            _ws.Close();
            _ws = null;
        }
    }

    void DoReconnect()
    {
        Disconnect();
        Connect();
    }

    public void SendJson(object payload)
    {
        if (_ws == null || !_ws.IsAlive) { Debug.LogWarning("[Hermes] Not connected"); return; }
        string json = JsonUtility.ToJson(payload);
        _ws.Send(json);
    }
    #endregion

    #region Agent → Engine commands
    // Dari agent: "kirim command spawn enemy"
    // Lu tinggal pake SendJson dari mana aja.

    /// <summary>
    /// Panggil dari Inspector Event atau script lain untuk reply ke agent.
    /// </summary>
    public void Respond(string id, object result)
    {
        SendJson(new { type = "response", id, result });
    }
    #endregion

    #region Agent messages handler (main thread)
    void OnMessageInternal(string raw)
    {
        try
        {
            Msg msg = JsonUtility.FromJson<Msg>(raw);
            Debug.Log($"[Hermes] ← type:{msg.type} action:{msg.action}");

            switch (msg.type)
            {
                case "command":
                    HandleCommand(msg.id, msg.action, msg.@params);
                    break;
                case "query":
                    HandleQuery(msg.id, msg.action, msg.@params);
                    break;
                case "config":
                    HandleConfig(msg.set);
                    break;
                default:
                    Debug.Log($"[Hermes] Unhandled type {msg.type}");
                    break;
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"[Hermes] Parse error: {ex.Message}");
        }
    }

    [System.Serializable]
    class Msg
    {
        public string type;
        public string id;
        public string action;
        public string @params; // raw JSON, parse manual
        public CfgSet set;
    }
    [System.Serializable] class CfgSet { public string skybox_color; public float time_of_day; }

    void HandleCommand(string id, string action, string paramJson)
    {
        switch (action)
        {
            case "spawn":
                var spawn = JsonUtility.FromJson<SpawnParams>(paramJson);
                Spawn(spawn.prefab_name, new Vector3(spawn.x, spawn.y, spawn.z));
                Respond(id, new { status = "spawned", name = spawn.prefab_name });
                break;

            case "move_camera":
                var cam = JsonUtility.FromJson<MoveCmd>(paramJson);
                Camera.main.transform.position = new Vector3(cam.x, cam.y, cam.z);
                Respond(id, new { status = "moved" });
                break;

            case "destroy_all":
                foreach (var go in GameObject.FindGameObjectsWithTag("AgentSpawned")) Destroy(go);
                Respond(id, new { status = "destroyed" });
                break;

            case "set_material_color":
                var mat = JsonUtility.FromJson<MatCmd>(paramJson);
                Renderer r = GameObject.Find(mat.object_name)?.GetComponent<Renderer>();
                if (r != null) r.material.color = HexToColor(mat.color);
                Respond(id, new { status = "set", color = mat.color });
                break;

            case "create_light":
                var l = JsonUtility.FromJson<LightCmd>(paramJson);
                var obj = new GameObject("AgentLight");
                var lt = obj.AddComponent<Light>();
                lt.type = (LightType)System.Enum.Parse(typeof(LightType), l.light_type, true);
                lt.color = HexToColor(l.color);
                lt.intensity = l.intensity;
                obj.transform.position = new Vector3(l.x, l.y, l.z);
                Respond(id, new { status = "created", name = obj.name });
                break;

            default:
                Debug.LogWarning($"[Hermes] Unknown command: {action}");
                Respond(id, new { error = "unknown_command", action });
                break;
        }
    }

    void HandleQuery(string id, string action, string paramJson)
    {
        switch (action)
        {
            case "get_objects":
                string[] names = new string[GameObject.FindObjectsOfType<GameObject>().Length];
                int i = 0;
                foreach (var go in GameObject.FindObjectsOfType<GameObject>()) names[i++] = go.name;
                Respond(id, new { objects = names });
                break;

            case "get_fps":
                Respond(id, new { fps = 1f / Time.unscaledDeltaTime });
                break;

            default:
                Respond(id, new { error = "unknown_query" });
                break;
        }
    }

    void HandleConfig(CfgSet cfg)
    {
        if (!string.IsNullOrEmpty(cfg.skybox_color))
            RenderSettings.skybox?.SetColor("_Tint", HexToColor(cfg.skybox_color));
    }

    #region Helpers
    static Color HexToColor(string hex)
    {
        ColorUtility.TryParseHtmlString(hex, out Color c);
        return c;
    }

    void Spawn(string prefabName, Vector3 pos)
    {
        // Ganti dengan Resource.Load<GameObject>(...) atau Addressables di production
        var go = new GameObject(prefabName + "_Agent");
        go.transform.position = pos;
        go.tag = "AgentSpawned";
        Debug.Log($"[Hermes] Spawned {go.name} at {pos}");
    }
    #endregion

    #region Payload classes (Unity JsonUtility needs explicit fields)
    [System.Serializable] public class SpawnParams   { public string prefab_name; public float x, y, z; }
    [System.Serializable] public class MoveCmd       { public float x, y, z; }
    [System.Serializable] public class MatCmd        { public string object_name; public string color; }
    [System.Serializable] public class LightCmd     { public string light_type; public string color; public float intensity; public float x, y, z; }
    #endregion
}
