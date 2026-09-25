import clsx from "clsx";
import { bgSurface, baseBorder, hoverShadow, animateFast } from "../../utils/style";

export const CardItem =({children, styleClass}) =>{
    return(
        <div className={clsx(
            bgSurface, animateFast, baseBorder, " shadow-md ", hoverShadow,
            styleClass, "hover:-translate-y-2"
        )}>
            {children}
        </div>
    )
}