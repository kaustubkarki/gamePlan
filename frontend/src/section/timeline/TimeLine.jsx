import "./timeline.css";
import timelineData from "./data";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

const Timeline = () => {
  return (
    <main className="w-full max-w-[699px] relative py-20 px-6 mx-auto bg-transparent z-1">
      <h1 className="text-3xl font-bold text-center mb-4 z-10">
        Our road to glory!
      </h1>
      <p className="text-center text-sm max-w-xs mx-auto mb-6 leading-relaxed">
        Below you can see a timeline how our server processes your video.
      </p>
      <div className=" bg-[#888893] absolute left-1/2 w-[0.15rem] h-[80%]"></div>
      {timelineData.map((item, index) => (
        <div
          key={item.id}
          className={`accomplishment bg-gray-300 p-4 rounded-sm shadow-md max-w-[300px] flex-1 text-sm mt-8 relative flex gap-1 ${
            index % 2 === 0 ? "right-side" : "left-side"
          }`}
        >
          <div className="corner w-4 h-4 bg-gray-300 transform rotate-45 absolute top-1/2 right-0 translate-y-[-50%]"></div>
          <p
            className={`label font-semibold text-xs py-1 px-2 rounded-sm ${item.className}`}
          >
            {item.label}
          </p>
          <div className="info max-w-[200px]">
            <p className="date opacity-50">
              <u>{item.date}</u>
            </p>
            <p className="accomplishment-description my-2 opacity-80">
              {item.description}
            </p>
            <button className="flex items-center gap-2 text-xs font-semibold">
              <HoverCard>
                <HoverCardTrigger className="text-blue-900">
                  Read more 📖
                </HoverCardTrigger>
                <HoverCardContent className="bg-[#042630] p-4 rounded-14 shadow-lg border border-gray-700 ">
                  <div className="flex flex-col items-start gap-2">
                    <ul className="list-disc list-inside mt-2 text-white text-left">
                      {item.points.map((point, i) => (
                        <li key={i} className="p-1 text-sm">
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                </HoverCardContent>
              </HoverCard>
              <p className="text-gray-500 opacity-80"></p>
            </button>
          </div>
        </div>
      ))}
    </main>
  );
};

export default Timeline;
