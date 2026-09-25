import { Eye, EyeClosed} from 'lucide-react';
import { useState } from "react";
import { baseBorder, baseText, animateSlow, baseBackground } from '../../utils/style';
import clsx from 'clsx';

export const Input = ({inputType, Icon, label, required = true, placeHolder, isPassword = false, value, onChange}) =>{
    const [ showPassword, setShowPassword] = useState(false);
    const changeModeType = () =>{
        setShowPassword(prevResult => !prevResult);
    };

    return (
        <div className={clsx('flex-col my-3', animateSlow)}>
            <p className='text-start text-base font-semibold'>
                {label}
            </p>
            <div className= {clsx(
                baseBorder, baseBackground, animateSlow, "border-2 items-center px-1 rounded-md flex relative",
            )}>
                <input
                    value={value}
                    onChange={onChange} 
                    required = {required}
                    placeholder={placeHolder}
                    type = { !isPassword 
                        ? inputType 
                        : (showPassword? "text" : "password")
                    }
                    className= {clsx(baseText, baseBackground, "transition-colors duration-500 ease-linear", "focus:outline-none indent-7 w-full p-2")}
                />

                <Icon className='text-primary absolute'/>
                
                {isPassword && (
                        <button type='button' aria-label='Hide or display password' onClick={changeModeType} className='cursor-pointer'>
                            {showPassword? <Eye/> : <EyeClosed/>}
                        </button>
                )}
            </div>
        </div>
    )
}