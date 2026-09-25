import { BrowserRouter, Routes, Route } from "react-router-dom";
import ManageRoutes from "./ManageRoute";
import Login from "../pages/Login";
import {ToastContainer} from 'react-toastify';

import 'react-toastify/dist/ReactToastify.css'; // Import CSS của thư viện Toastify

const  AppRoutes= () =>{
    return(
        <BrowserRouter>
            <ToastContainer theme="colored" position="top-right" autoClose={2500}/>
            <Routes>
                {/* ================================================== */}
                {/* TRANG ĐỘC LẬP: Không Navbar, Không Sidebar         */}
                {/* ================================================== */}
                <Route 
                    path="/log-in" 
                    element={
                        <Login/>
                    }
                />

                {/* ================================================== */}
                {/* TRANG CHO MANAGER (HEADER, FOOTER, CÁC NỘI DUNG....)*/}
                {/* ================================================== */}
                <Route>
                    <Route path="/*" element={<ManageRoutes/>}/>
                </Route>
            </Routes>
        </BrowserRouter>
    )
};
export default AppRoutes;
