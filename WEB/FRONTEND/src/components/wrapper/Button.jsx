import clsx from "clsx";
import {animateFast} from "../../utils/style";

export const Button =({children, style: styleClass}) =>{
    return(
        <div className={clsx(
            animateFast, styleClass,
            "bg-primary text-white font-semibold hover:bg-primary-hover hover:scale-95"
        )}>
            {children}
        </div>
    )
}
