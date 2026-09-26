import { useAuth } from "../hooks/useAuth";
import {Navigate, Outlet} from 'react-router-dom';

export const AuthProtected = () =>{
    // Không đăng nhập thì cho cook về trang Login
    const {isAuthenticated} = useAuth();
    if (!isAuthenticated){
        return <Navigate to={"/log-in"} replace/>
    }
    return <Outlet/>
}