import { Element } from "react-scroll";
import Timeline from "./timeline/TimeLine.jsx";

const Features = () => {
  return (
    <section>
      <Element name="features">
        <div className="container">
          <div className="relative flex md:flex-wrap flex-nowrap border-2 border-s3 rounded-7xl md:overflow-hidden max-md:flex-col feature-after md:g7 max-md:border-none max-md:rounded-none max-md:gap-3">
            <Timeline />
          </div>
        </div>
      </Element>
    </section>
  );
};
export default Features;
