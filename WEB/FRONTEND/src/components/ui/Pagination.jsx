import clsx from "clsx";

import { ChevronRight } from 'lucide-react';
import { ChevronLeft } from 'lucide-react';

import { baseBorder, animateFast, } from "../../utils/style";


export const Pagination = ({current_page, count_page, onChangeIndexPage}) =>{
    let list_page_index = []
    list_page_index.push(<PagePrev key={`page-index-prev`} current_page={current_page} onChangeIndexPage={onChangeIndexPage}/>)
    for (let i = 1; i<count_page+1; i++){
        list_page_index.push(
            <PageIndex 
                key={`page-index-${i}`} page_num={i} 
                current_page={current_page} 
                onChangeIndexPage={onChangeIndexPage}
            />
        )
    }
    list_page_index.push(<PageNext key={`page-index-next`} current_page={current_page} count_page={count_page} onChangeIndexPage={onChangeIndexPage}/>)

    return (
        <div className="flex gap-2 justify-center">
            {list_page_index}
        </div>
    )
}

const PageIndex = ({current_page, page_num, onChangeIndexPage}) =>{
    // console.log(current_page);
    return(
        <span className={clsx( "border-2", baseBorder, animateFast,
            " flex justify-center text-lg items-center px-3 py-1 rounded-md cursor-pointer",
            page_num === current_page && " bg-primary text-dark-text font-bold"
        )}
        onClick={()=>{onChangeIndexPage(page_num)}} 
        >
            {page_num}
        </span>
    )
}

const PagePrev = ({current_page, onChangeIndexPage}) =>{
    const handleChangePrev = () =>{
        if (current_page >1){
            onChangeIndexPage(current_page-1);
        }
    }
    return(
        <span
            className={clsx( baseBorder, "border-2",
                "flex justify-center items-center p-2 rounded-md bg-primary/40 cursor-pointer",
                current_page==1 ? "opacity-40 cursor-not-allowed" : " opacity-100"
            )}
            onClick={handleChangePrev} 
        >
            <ChevronLeft size={20} strokeWidth={2.5}/>
        </span>
    )
}

const PageNext = ({current_page, count_page, onChangeIndexPage}) =>{
    const handleChangeNext = () =>{
        if (current_page < count_page){
            onChangeIndexPage(current_page + 1);
        }
    }
    return(
        <span
            className={clsx(baseBorder, "border-2",
                "flex justify-center items-center p-2 rounded-md bg-primary/40 cursor-pointer",
                current_page==count_page ? "opacity-40 cursor-not-allowed" : " opacity-100"
            )}
            onClick={handleChangeNext} 
        >
            <ChevronRight size={20} strokeWidth={2.5}/>
        </span>
    )
}