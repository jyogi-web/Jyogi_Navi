import { Live2DViewer } from "@/features/live2d/Live2DViewer";

export default function Live2DPage() {
  return (
    <div className="relative h-screen w-screen overflow-hidden bg-transparent">
      <Live2DViewer modelPath="/live2d/usako/ねここ.model3.json" />
    </div>
  );
}
