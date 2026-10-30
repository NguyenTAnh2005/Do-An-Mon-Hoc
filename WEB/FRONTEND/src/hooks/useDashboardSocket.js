import { useEffect, useState } from "react";
import { buildDashBoardSocketURL } from "../services/dashBoardSocket";

export const useDashboardSocket = (onMessage) =>{
    const [status, setStatus] = useState("connecting");

    useEffect(()=>{
        const ws = new WebSocket(buildDashBoardSocketURL());

        ws.onopen = () =>{
            console.log("[WS] open");
            setStatus("open");
        };

        ws.onmessage = (event) =>{
            const message = JSON.parse(event.data);
            console.log("[WS] message: ", message);
            onMessage(message);
        };
        
        ws.onerror = () =>{
            console.log("[WS] error");
        }

        ws.onclose = (event) =>{
            console.log("[WS] close:", event.code, event.reason);
            setStatus("closed");
        }
    },[]);
    return {status};
}