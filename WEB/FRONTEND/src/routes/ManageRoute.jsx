import { Routes, Route } from "react-router-dom";

import Dashboard from "../pages/Dashboard";
import History from "../pages/History";
import Statistics from "../pages/Statistics";
import NotFound from "../pages/NotFound";

import Layout from "../layout/Layout";

const ManageRoutes = () =>{
    return(
        <Routes>
            <Route element={<Layout/>}>
                <Route index element={<Dashboard/>}/>
                <Route path="history" element={<History/>}/>
                <Route path="stats" element={<Statistics/>}/>
            </Route>
            <Route path="*" element={<NotFound/>}/>
        </Routes>
    )
};

export default ManageRoutes;