import manualInstance from "./config/manualConfig";

const END_POINT = '/dashboard';

export const dashboardService = {
    getSnapshot: async () => {
        const response = await manualInstance.get(`${END_POINT}/snapshot`);
        return response;
    }
};