import { useEffect } from 'react';
import { useState } from 'react';

export default function DomainManager() {
    const [domains, setDomains] = useState([]);
    const [activeTab, setActiveTab] = useState('manage');
    const [adds, setAdds] = useState('');
    const [dels, setDels] = useState('');
    const [rules, setRules] = useState('');

    const handleSubmitManage = (e) => {
        e.preventDefault();
        fetch('/api/domain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ adds, dels }),
        });
    };

    const handleSubmitImport = (e) => {
        e.preventDefault();
        fetch('/api/domain', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ rules }),
        });
    };
    useEffect(async () => {
        const response = await fetch('/api/domain');
        const data = await response.json();
        setDomains(data);
    }, []);
    return (
        <div className='flex h-screen'>
            <div className='w-96 min-w-[18rem] border-r flex flex-col'>
                <div className='flex border-b'>
                    <button
                        onClick={() => setActiveTab('manage')}
                        className={`flex-1 px-4 py-2 text-sm font-medium ${
                            activeTab === 'manage'
                                ? 'bg-white border-b-2 border-blue-600 font-semibold'
                                : 'bg-gray-100'
                        }`}>
                        Manage Domains
                    </button>
                    <button
                        onClick={() => setActiveTab('import')}
                        className={`flex-1 px-4 py-2 text-sm font-medium ${
                            activeTab === 'import'
                                ? 'bg-white border-b-2 border-blue-600 font-semibold'
                                : 'bg-gray-100'
                        }`}>
                        Import Rules
                    </button>
                </div>

                <div className='overflow-y-auto p-5 flex-1'>
                    {activeTab === 'manage' && (
                        <form onSubmit={handleSubmitManage}>
                            <label className='block mb-2 font-medium'>
                                Add Domains (one per line):
                            </label>
                            <textarea
                                className='w-full h-32 font-mono p-2 border mb-4'
                                value={adds}
                                onChange={(e) => setAdds(e.target.value)}
                            />
                            <label className='block mb-2 font-medium'>
                                Delete Domains (one per line):
                            </label>
                            <textarea
                                className='w-full h-32 font-mono p-2 border mb-4'
                                value={dels}
                                onChange={(e) => setDels(e.target.value)}
                            />
                            <button
                                type='submit'
                                className='px-4 py-2 bg-blue-600 text-white rounded'>
                                Submit
                            </button>
                        </form>
                    )}

                    {activeTab === 'import' && (
                        <form onSubmit={handleSubmitImport}>
                            <label className='block mb-2 font-medium'>
                                Import SwitchyOmega Rules:
                            </label>
                            <textarea
                                className='w-full h-48 font-mono p-2 border mb-4'
                                placeholder='*.google.com +proxy&#10;*.chatgpt.com +proxy'
                                value={rules}
                                onChange={(e) => setRules(e.target.value)}
                            />
                            <button
                                type='submit'
                                className='px-4 py-2 bg-blue-600 text-white rounded'>
                                Import
                            </button>
                        </form>
                    )}
                </div>
            </div>

            <div className='flex-1 p-5 overflow-y-auto bg-gray-50'>
                <h2 className='text-xl font-semibold mb-4'>
                    Domain List - {domains.length}
                </h2>
                <ul className='grid grid-cols-[repeat(auto-fit,minmax(12rem,1fr))] gap-2 pl-4 list-decimal list-inside'>
                    {domains.map((domain, index) => (
                        <li
                            key={index}
                            className='bg-white font-mono p-2 border rounded text-sm'>
                            {domain}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
