import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';

import Home from './pages/Home';
import DomainManager from './pages/DomainManager';
export default function App() {
    return (
        <HashRouter>
            <Routes>
                <Route path='/' element={<Home />} />
                <Route path='/domain' element={<DomainManager />} />
                <Route path='*' element={<Navigate to='/' />} />
            </Routes>
        </HashRouter>
    );
}
