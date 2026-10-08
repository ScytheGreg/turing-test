(function (root, factory) {
    const api = factory();

    if (typeof module === "object" && module.exports) {
        module.exports = api;
    } else {
        root.DisplayConfig = api;
    }
})(typeof window !== "undefined" ? window : globalThis, () => {
    const DEFAULT_SESSIONS = ["alice", "bob"];

    function normalizeSession(value) {
        const session = (value || "").trim().toLowerCase();
        return DEFAULT_SESSIONS.includes(session) ? session : null;
    }

    function normalizeName(value, fallback) {
        const name = (value || "").trim();
        return name || fallback.toUpperCase();
    }

    function getDisplayConfig(search = "") {
        const params = new URLSearchParams(search);
        const left = normalizeSession(params.get("left")) || DEFAULT_SESSIONS[0];
        let right = normalizeSession(params.get("right")) || DEFAULT_SESSIONS[1];

        if (left === right) {
            right = DEFAULT_SESSIONS.find((session) => session !== left);
        }

        return {
            left,
            right,
            leftName: normalizeName(params.get("leftName"), left),
            rightName: normalizeName(params.get("rightName"), right),
        };
    }

    return { getDisplayConfig };
});
