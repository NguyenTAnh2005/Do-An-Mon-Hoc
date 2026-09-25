import clsx from "clsx";
import { Link } from "react-router-dom";
import { Frown } from "lucide-react";

import { Button } from "../components/wrapper/Button";
import { baseTextBg, sectionTitle, mutedText, animateSlow } from "../utils/style";

const NotFound = () => {
    return (
        <div className={clsx(baseTextBg, animateSlow, "min-h-screen flex items-center justify-center px-4")}>
            <div className="flex flex-col items-center text-center gap-4">
                <span className="bg-primary/10 text-primary p-5 rounded-full">
                    <Frown size={40} />
                </span>
                <h1 className={sectionTitle}>404</h1>
                <p className={clsx(mutedText, "text-base max-w-sm")}>
                    Trang bạn tìm không tồn tại hoặc đã bị di chuyển.
                </p>
                <Link to="/">
                    <Button style="px-6 py-3 rounded-md cursor-pointer">
                        Quay về Dashboard
                    </Button>
                </Link>
            </div>
        </div>
    );
};

export default NotFound;