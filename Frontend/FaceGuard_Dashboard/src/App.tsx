/*import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'*/
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css';
import Login from './Login/login';
//import Message from "./test_react/test"; 
import Home from "./Home/home"; 
import Account from "./Account/account";
import Permissions from "./Permissions/permissions";
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<Home />} />
        <Route path="/account" element={<Account />} />
        <Route path="/permissions" element={<Permissions />} />
      </Routes>
    </Router>
  );
}

export default App;

