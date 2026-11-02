import { useEffect, useState } from "react";
import { buildDashBoardSocketURL } from "../services/dashBoardSocket";
import { authService } from "../services/auth";
import { tokenManager } from "../services/tokenManager";

export const useDashboardSocket = (onMessage, onReconnected) =>{
    const [status, setStatus] = useState("connecting");

    useEffect(()=>{
        let stopped = false;
        let ws = null;
        let timerId = null;
        let retryCount = 0;
        let hasOpenedBefore = false;
        let hasRefreshedForClose = false;   // đã thử refresh cho đợt 1008 hiện tại chưa
        
        const connect = () =>{
            setStatus("connecting");
            ws = new WebSocket(buildDashBoardSocketURL());

            ws.onopen = () =>{
                retryCount = 0;
                hasRefreshedForClose = false;
                setStatus("open");
                console.log("[WS] open");
                if (hasOpenedBefore && onReconnected){
                    onReconnected();
                }
                hasOpenedBefore = true;
            };

            ws.onmessage = (event) =>{
                const message = JSON.parse(event.data);
                onMessage(message);
                console.log("[WS] message: ", message);
            };
            
            ws.onerror = () =>{
                console.log("[WS] error");
            }

            ws.onclose = (event) =>{
                console.log("[WS hook] onclose, code =", event.code, "stopped =", stopped);
                if (stopped){
                    return; // chủ động đóng, không tự kết nối lại.
                }
                if (event.code == 1008){
                    // Lỗi sai token
                    setStatus("closed");
                    console.log("[WS] closed. Invalid Token.");
                    return;
                }
                setStatus("reconnecting");
                console.log("[WS] reconnecting.");
                let delay = 1000;
                for (let i = 0; i< retryCount; i++){
                    delay = delay*2;
                }
                if (delay>30000){
                    delay = 30000;
                }
                retryCount = retryCount+1;
                timerId=setTimeout(connect, delay);
            };
        }

        connect();

        return () =>{
            // Chủ động closed khi components bị unmount.
            console.log("[WS hook] cleanup chạy, readyState =", ws ? ws.readyState : "chưa có ws"); 
            stopped = true;
            clearTimeout(timerId);
            if (ws){
                ws.close();
            }
        };
    },[]);
    return {status};
}