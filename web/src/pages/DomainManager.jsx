import { useEffect, useState } from "react";

export default function DomainManager() {
  const [domains, setDomains] = useState([]);
  const [activeTab, setActiveTab] = useState("manage");
  const [adds, setAdds] = useState("");
  const [dels, setDels] = useState("");
  const [rules, setRules] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const getDomainList = async () => {
    const response = await fetch("/api/domain");
    const data = await response.json();
    setDomains(data);
  };

  const handleSubmitManage = (e) => {
    e.preventDefault();
    fetch("/api/domain", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ adds, dels }),
    });
    getDomainList();
  };

  const handleSubmitImport = (e) => {
    e.preventDefault();
    fetch("/api/domain/import", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ rules }),
    });
    getDomainList();
  };

  useEffect(() => {
    getDomainList();
  }, []);

  return (
    <div className="flex h-screen text-sm text-gray-800 bg-gray-100">
      {/* Sidebar */}
      <div
        className={`transition-all duration-300 bg-white border-r shadow-sm ${
          sidebarOpen ? "w-full md:w-80" : "w-0"
        } overflow-hidden`}
      >
        <div className="h-full flex flex-col">
          <div className="flex justify-between items-center px-4 py-3 border-b">
            <h1 className="text-lg font-semibold">Domain Manager</h1>
            <button
              className="md:hidden text-gray-500"
              onClick={() => setSidebarOpen(false)}
            >
              ×
            </button>
          </div>

          {/* Tabs */}
          <div className="flex justify-center border-b">
            <button
              className={`flex-1 py-2 text-center ${
                activeTab === "manage"
                  ? "border-b-2 border-blue-500 text-blue-600 font-semibold"
                  : "text-gray-500"
              }`}
              onClick={() => setActiveTab("manage")}
            >
              Manage
            </button>
            <button
              className={`flex-1 py-2 text-center ${
                activeTab === "import"
                  ? "border-b-2 border-blue-500 text-blue-600 font-semibold"
                  : "text-gray-500"
              }`}
              onClick={() => setActiveTab("import")}
            >
              Import
            </button>
          </div>

          <div className="p-4 overflow-y-auto flex-1">
            {activeTab === "manage" && (
              <form onSubmit={handleSubmitManage} className="space-y-4">
                <div>
                  <label className="block font-medium mb-1">Add Domains</label>
                  <textarea
                    className="w-full p-2 border rounded font-mono resize-none"
                    rows={5}
                    value={adds}
                    onChange={(e) => setAdds(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block font-medium mb-1">
                    Delete Domains
                  </label>
                  <textarea
                    className="w-full p-2 border rounded font-mono resize-none"
                    rows={5}
                    value={dels}
                    onChange={(e) => setDels(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
                >
                  Submit Changes
                </button>
              </form>
            )}

            {activeTab === "import" && (
              <form onSubmit={handleSubmitImport} className="space-y-4">
                <div>
                  <label className="block font-medium mb-1">
                    SwitchyOmega Rules
                  </label>
                  <textarea
                    className="w-full p-2 border rounded font-mono resize-none"
                    rows={10}
                    placeholder="*.google.com +proxy&#10;*.chatgpt.com +proxy"
                    value={rules}
                    onChange={(e) => setRules(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
                >
                  Import Rules
                </button>
              </form>
            )}
          </div>
        </div>
      </div>

      {/* Main */}
      <div className="flex-1 flex flex-col p-4 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold">
            Total Domains: {domains.length}
          </h2>
          <button
            className="md:hidden text-sm text-blue-600 underline"
            onClick={() => setSidebarOpen(true)}
          >
            Open Sidebar
          </button>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
          {domains.map((domain, index) => (
            <div
              key={index}
              className="bg-white p-2 border rounded font-mono text-xs truncate"
              title={domain}
            >
              {domain}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
