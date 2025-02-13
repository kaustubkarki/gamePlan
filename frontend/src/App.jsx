import Demo from "./section/Demo";
import Faq from "./section/Faq";
import Features from "./section/Features";
import Footer from "./section/Footer";
import Header from "./section/Header";
import Hero from "./section/Hero";
import Slider from "./section/Slider";
import VideoUploader from "./section/VideoUploader";

const App = () => {
  return (
    <main className="overflow-hidden">
      <Header />
      <Hero />
      <Features />
      <VideoUploader />
      <Slider />
      <Faq />
      <Demo />
      <Footer />
    </main>
  );
};

export default App;
