import { Routes, Route } from "react-router-dom";

import Dashboard from "../pages/Dashboard";
import ClassificationHistory from "../pages/ClassificationHistory";
import Statistics from "../pages/Statistics";
import ClassificationDetail from "../pages/ClassificationDetail";
import { Overview } from "../pages/statistics/Overview"
import { ByArea } from "../pages/statistics/ByArea";
import { Timeline } from "../pages/statistics/Timeline";
import { Accuracy } from "../pages/statistics/Accuracy";

import NotFound from "../pages/NotFound";

import Layout from "../layout/Layout";

const ManageRoutes = () =>{
    return(
        <Routes>
            <Route element={<Layout/>}>
                <Route index element={<Dashboard/>}/>
                <Route path="history" element={<ClassificationHistory/>}/>
                <Route path="stats" element={<Statistics/>}>
                    <Route index element={<Overview/>}/>
                    <Route path="by-area" element={<ByArea/>}/>
                    <Route path="timeline" element={<Timeline/>}/>
                    <Route path="accuracy" element={<Accuracy/>}/>
                </Route>
                <Route path="history/:id" element={<ClassificationDetail/>}/>
            </Route>
            <Route path="*" element={<NotFound/>}/>
        </Routes>
    )
};

export default ManageRoutes;