import * as React from "react";
import Autoplay from "embla-carousel-autoplay";
import { Card, CardContent } from "@/components/ui/card";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";

const slides = [
  {
    title: "Slide 1",
    image: "/images/slider/performance.png",
    description: "This is the first slide description.",
  },
  {
    title: "Slide 2",
    image: "/images/slider/Kmeans.png",
    description: "This is the second slide description.",
  },
  {
    title: "Slide 3",
    image: "/images/slider/performance.png",
    description: "This is the third slide description.",
  },
  {
    title: "Slide 4",
    image: "/images/slide4.jpg",
    description: "This is the fourth slide description.",
  },
  {
    title: "Slide 5",
    image: "/images/slide5.jpg",
    description: "This is the fifth slide description.",
  },
];

const Slider = () => {
  const plugin = React.useRef(
    Autoplay({ delay: 2000, stopOnInteraction: true })
  );

  return (
    <section>
      <div className="container my-16 ">
        <h1 className="mb-2 h1 text-p4 uppercase max-lg:mb-2 max-lg:h2 max-md:mb-2 max-md:text-5xl max-md:leading-12">
          Analytics of our model
        </h1>
        <p className="max-w-fit mb-6 body-1 max-md:mb-10 mx-auto">
          Get to know about how your performance is being analyzed with
          analytics of our model.
        </p>
        <div className="flex items-center justify-center overflow-visible">
          <Carousel
            plugins={[plugin.current]}
            className="w-full max-w-8xl"
            onMouseEnter={plugin.current.stop}
            onMouseLeave={plugin.current.reset}
            opts={{ align: "start" }}
          >
            <CarouselContent className="flex">
              {slides.map((slide, index) => (
                <CarouselItem
                  key={index}
                  className="md:basis-1/2 sm:basis-1/2 basis-full"
                >
                  <div className="p-2">
                    {/* Make Card Expand on Click */}
                    <Card className="shadow-md bg-blue-800 rounded-xl relative transition-all duration-300 max-h-[800px]">
                      <CardContent className="p-4 relative">
                        <img
                          src={slide.image}
                          alt={slide.title}
                          className="w-full h-80 object-contain rounded-lg mb-3 cursor-pointer transition-transform duration-300"
                        />
                        <h1 className="text-lg font-semibold text-gray-200">
                          {slide.title}
                        </h1>
                        <p className="text-sm text-gray-300">
                          {slide.description}
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                </CarouselItem>
              ))}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
          </Carousel>
        </div>
      </div>
    </section>
  );
};

export default Slider;
