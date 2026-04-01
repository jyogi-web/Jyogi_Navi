"use client";

import { useEffect, useRef } from "react";

interface Props {
  modelPath: string;
}

export function Live2DViewer({ modelPath }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    let app: import("pixi.js").Application | null = null;

    async function init() {
      console.log("[Live2D] init start");

      const PIXI = await import("pixi.js");
      console.log("[Live2D] pixi loaded:", PIXI.VERSION);

      const { Live2DModel } = await import("pixi-live2d-display/cubism4");
      console.log("[Live2D] Live2DModel loaded");

      Live2DModel.registerTicker(PIXI.Ticker);

      const w = window.innerWidth;
      const h = window.innerHeight;

      app = new PIXI.Application({
        view: canvas,
        width: w,
        height: h,
        backgroundAlpha: 0,
        antialias: true,
        autoDensity: true,
        resolution: window.devicePixelRatio || 1,
      });
      console.log("[Live2D] PIXI app created, size:", w, h);

      console.log("[Live2D] loading model from:", modelPath);
      const model = await Live2DModel.from(modelPath, { autoInteract: false });
      console.log("[Live2D] model loaded, size:", model.width, model.height);

      app.stage.addChild(model as unknown as import("pixi.js").DisplayObject);

      const scale = Math.min(
        (w / model.internalModel.originalWidth) * 0.9,
        (h / model.internalModel.originalHeight) * 0.9
      );
      model.scale.set(scale);
      model.anchor.set(0.5, 0.5);
      model.x = w / 2;
      model.y = h / 2;
      console.log("[Live2D] model positioned, scale:", scale, "x:", model.x, "y:", model.y);
    }

    init().catch((e) => console.error("[Live2D] error:", e));

    const handleResize = () => {
      if (!app) return;
      app.renderer.resize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      app?.destroy(false, { children: true });
    };
  }, [modelPath]);

  return <canvas ref={canvasRef} className="h-full w-full" style={{ touchAction: "none" }} />;
}
