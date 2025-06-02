import { HashRouter, Navigate, Route, Routes } from 'react-router-dom'

import DomainManager from './pages/DomainManager'
import Home from './pages/Home'

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/domain" element={<DomainManager />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </HashRouter>
  )
}
