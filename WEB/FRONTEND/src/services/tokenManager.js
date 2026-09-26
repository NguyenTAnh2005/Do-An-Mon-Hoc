let accessToken = null;
// Khai báo object lưu trữ access_token để sử dụng ở các file config hay nằm ngoài JSX
//  Cơ chế pub sub khá giống như bên giao tiếp iot mqtt
//  Khai báo mảng chứa các func đã subrice vào (vd: setAccessToken bên Auth)
// Các publish như set hay clear, khi chạy thì sẽ gọi các func đã subrice này giúp cập nhật ở bên kia. 
let listeners = [];

export const tokenManager = {
    // Đăng ký hàm subcribe
    subcribe: (funct) =>{
        listeners.push(funct);
    },
    // Xóa bỏ hàm subcribe cũ
    unSubcribe: (funct) =>{
        let unSubIndex = listeners.indexOf(funct);
        // Xóa 1 phần tử kể từ vị trí unSubcribe
        //  Nếu không tìm thấy thì JS trả về -1, cần set đk cho TH này
        if (unSubIndex!==-1){
            listeners.splice(unSubIndex, 1);
        }
    },
    get: () => {
        return accessToken
    },
    // Publish cập nhật token ở object này và cập nhật dựa theo 
    // hàm dã sub giúp bên sub có khả năng cập nhật theo
    setTwoSide: (token) =>{
        accessToken = token;
        listeners.forEach((callbackFn)=>{
            callbackFn(token);
        });
    },
    //  Sử dụng khi chỉ muốn cập nhật ở mỗi bên này, bên sub không cần cập nhật theo.
    setOneSide: (token)=>{
     accessToken = token;   
    },
    // Clear thường thì bên Authcontext sẽ clear trước sau đó 
    // gọi bên này nên không nhất thiết phải duyệt sub như bên set.
    clear: ()=>{
        accessToken = null;
    }
}