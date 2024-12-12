import { Element } from "react-scroll";
import { links } from "../constants/index.jsx";
import { Marker } from "../components/Marker.jsx";

const Demo = () => {
  return (
    <section>
      <Element
        name="demo"
        className="g7 relative pb-32 pt-24 max-lg:pb-24 max-md:py-16"
      >
        <div className="container">
          <div className="flex items-center">
            <div className="relative mr-6 flex-540 max-xl:flex-280 max-lg:flex256 max-md:flex-100">
              <div className="mb-10 flex flex-row items-center justify-start gap-4">
                <img src="/vite.svg" width={80} height={55} alt="gamePlan" />
                <span className="h1 text-p4 uppercase max-lg:mb-7 max-lg:h2 max-md:mb-4 max-md:text-4xl max-md:leading-12">
                  gamePlan
                </span>
              </div>

              <p className="body-1 mb-10 max-w-md">
                Try it now for free - magic in your hand with power of python,
                javaScript, YOLO and MachineLearning.
              </p>

              <ul className="flex flex-wrap items-center gap-6">
                {links.map(({ id, url, icon }) => (
                  <li
                    key={id}
                    className="download_tech-link download_tech-link_last-before download_tech-link_last-after"
                  >
                    <a
                      href={url}
                      className="size-22 download_tech-icon_before relative flex items-center justify-center rounded-half border-2 border-s3 bg-s1 transition-borderColor duration-500"
                    >
                      <span className="absolute -top-2 rotate-90">
                        <Marker />
                      </span>
                      <img
                        src={"/images/lines.svg"}
                        alt="lines"
                        className="absolute size-13/20 object-contain"
                      />
                      <span className="download_tech-icon">{icon}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            <div className="mb-10 max-md:hidden">
              <div className="download_preview-before download_preview-after rounded-40 relative w-[955px] border-2 border-s5 p-6">
                <div className="relative rounded-3xl bg-s1 px-6 pb-6 pt-14">
                  <span className="download_preview-dot left-6 bg-p2" />
                  <span className="download_preview-dot left-11 bg-s3" />
                  <span className="download_preview-dot left-16 bg-p1/15" />

                  <video
                    src="/demo.mp4"
                    width={855}
                    height={655}
                    alt="screen"
                    className="rounded-xl"
                    autoPlay
                    muted
                    loop
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </Element>
    </section>
  );
};
export default Demo;
