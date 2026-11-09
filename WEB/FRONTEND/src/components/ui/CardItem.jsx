import clsx from "clsx";
import { bgSurface, baseBorder, animateFast } from "../../utils/style";

export const CardItem = ({ children, styleClass }) => {
    return (
        <div className={clsx(
            bgSurface, animateFast, baseBorder, styleClass
        )}>
            {children}
        </div>
    );
};