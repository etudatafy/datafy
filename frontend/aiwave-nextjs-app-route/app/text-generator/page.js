import BackToTop from "../backToTop";
import TextGeneratorPage from "./index";

export const metadata = {
  title: "Destek AL AI - Yapay Zeka Destekli Metin Üretici",
  description: "Destek AL AI - Yapay Zeka ile metin üretme ve içerik oluşturma aracı",
};

export default function TextGenerator() {
  return (
    <>
      <TextGeneratorPage />
      <BackToTop />
    </>
  );
}
