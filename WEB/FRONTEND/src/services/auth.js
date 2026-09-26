import  manualInstance from "./config/manualConfig";
import  autoInstance from "./config/autoConfig";

const END_POINT = '/auth';

export const authService = {
    login: async (email, password) =>{
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await autoInstance.post(`${END_POINT}/login`, formData, {headers:{'Content-Type': 'application/x-www-form-urlencoded'}});
        return response;
    },

    refreshToken: async()=>{
        const response = await autoInstance.post(`${END_POINT}/refresh-access-token`);
        return response;
    },

    logOut: async() =>{
        const response = await autoInstance.post(`${END_POINT}/logout`);
        return response;
    },

    getMe: async () =>{
        const response = await manualInstance.get(`${END_POINT}/get-me`);
        return response;
    },

    clean: async () =>{
        const response = await manualInstance.post(`${END_POINT}/clean-token`);
        return response;
    }
}