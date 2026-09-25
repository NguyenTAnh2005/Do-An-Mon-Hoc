import { motion } from "framer-motion";
import { Frown, Annoyed, ArrowRight} from "lucide-react";
import clsx from 'clsx';
import { animateFast, animateSlow, baseBorder, bgSurface, mutedText } from "../../utils/style";

export const StatusLoading = () =>{
    return(
        <div className={clsx(
            animateSlow, "p-6 flex flex-col justify-center items-center gap-5"
        )}>
            {/* PHẦN 1: 2 VÒNG LOAD TRONG VÀ NGOÀI, QUAY NGƯỢC CHIỀU NHAU */}
            <div className=" relative flex w-14 h-14 items-center justify-center">
                {/* Vòng LOAD TO */}
                <motion.div 
                    className={clsx(
                        "absolute border-4 border-solid inset-0 rounded-full",
                        "border-primary/20 border-t-primary",
                        "dark:border-white/20 dark:border-t-white"
                    )}
                    animate={{rotate:360}}
                    transition={{duration:1.5, repeat:Infinity, ease: "linear"}}
                />
                {/* Vòng LOAD NHỎ HƠN */}
                <motion.div 
                    className={clsx(
                        "absolute border-4 border-solid inset-3 rounded-full",
                        "border-primary/10 border-b-primary",
                        "dark:border-white/10 dark:border-b-white"
                    )}
                    animate={{rotate:-360}}
                    transition={{duration:1, repeat:Infinity, ease: "linear"}}
                />
            </div>
            {/* PHẦN 2: THÔNG ĐIỆP MESSAGE */}
            <div className={clsx(
                "flex items-center gap-2 text-2xl"
            )}>
                {/* Text với dots nhảy tuần tự thay vì đứng yên - CLAUDE*/}
                <div className="flex items-center gap-1 text-2xl">
                    <motion.span
                    initial={{ opacity: 0.4 }}
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
                    >
                    Waiting to load data
                    </motion.span>
                    {[0, 1, 2].map((i) => (
                    <motion.span
                        key={i}
                        className="inline-block font-bold"
                        animate={{ y: [0, -6, 0] }}
                        transition={{
                        duration: 1,
                        repeat: Infinity,
                        delay: i * 0.15,
                        ease: "easeInOut",
                        }}
                    >
                        .
                    </motion.span>
                    ))}
                </div>
            </div>
        </div>
    )
}

export const ContactButton = ({baseClass}) =>{
    return(
        <a href="https://www.facebook.com/tuan.anh.514281/?locale=vi_VN" target="blank" rel="noopener noreferrer"
        className={clsx(animateFast, baseClass, "hover:cursor-pointer flex justify-center gap-2 p-2 rounded-md font-semibold")}>
            <ArrowRight />
            <span>
                Contact support here.
            </span>
        </a>
    )
}
export const ReloadButton = ({baseClass}) =>{
    return(
        <div 
            onClick={()=>{location.reload()}}
            className={clsx(animateFast, baseClass, " hover:cursor-pointer flex justify-center gap-2 p-2 rounded-md font-semibold")}
        >
            <ArrowRight />
            <span>
                Reload the content.
            </span>
        </div>
    )
}

export const StatusError = ({message}) =>{
    return(
        <div className="flex justify-center h-[50vh] items-center">
            <div className= {clsx(
                bgSurface, baseBorder, animateSlow, 
                "flex flex-col items-center max-w-md border-2 w-full p-8 rounded-xl gap-4"
            )}>
                <div className="bg-red-100 text-red-600  p-4 rounded-full">
                    <Frown size={40}/>
                </div>
                <div className="flex flex-col items-center gap-2">
                    <span className="text-xl text-red-800 dark:text-red-600 font-bold">
                        Oops! Some thing went wrong.
                    </span>
                    <span className="text-base text-red-400">
                        {message}
                    </span>
                </div>
                <ContactButton
                baseClass={"bg-red-200 text-red-600 hover:bg-red-600 hover:text-red-200 mt-4"}
                />

            </div>
        </div>
    )
}

export const StatusNoData = () =>{
    return(
        <div className="flex justify-center h-[50vh] items-center">
            <div className= {clsx(
                bgSurface, baseBorder, animateSlow, 
                "flex flex-col items-center max-w-md border-2 w-full p-8 rounded-xl gap-4"
            )}>
                <div className="bg-gray-200 text-gray-600 p-4 rounded-full">
                    <Annoyed size={40}/>
                </div>
                <div className="flex flex-col items-center gap-2 text-center">
                    <span className="text-xl text-gray-800 dark:text-gray-200 font-bold">
                        No Data Available
                    </span>
                    <span className={clsx(mutedText,"text-base")}>
                        The connection is okay but there're no data from response.
                    </span>
                </div>

                <ReloadButton
                    baseClass={"bg-gray-200 text-gray-600 hover:bg-gray-600 hover:text-gray-200 mt-4"}
                />
            </div>
        </div>
    )
}