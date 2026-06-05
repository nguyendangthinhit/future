"use client";

import { cn } from "@/lib/utils";
import type { UploadedImage } from "@/lib/types";
import { ImagePlus, X } from "lucide-react";
import { useRef } from "react";

const MAX_IMAGES = 5;
const MAX_SIZE = 10 * 1024 * 1024;

export function ImageUploader({
  images,
  onChange,
}: {
  images: UploadedImage[];
  onChange: (images: UploadedImage[]) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFiles(files: FileList | null) {
    if (!files) return;
    const remainingSlots = MAX_IMAGES - images.length;
    const acceptedFiles = Array.from(files).slice(0, remainingSlots);

    acceptedFiles.forEach((file) => {
      if (file.size > MAX_SIZE) return;
      if (!/^image\/(jpeg|png|webp)$/.test(file.type)) return;

      const reader = new FileReader();
      reader.onload = () => {
        onChange([
          ...images,
          {
            id: crypto.randomUUID(),
            name: file.name,
            dataUrl: reader.result as string,
            size: file.size,
            file,
          },
        ]);
      };
      reader.readAsDataURL(file);
    });
  }

  function removeImage(id: string) {
    onChange(images.filter((image) => image.id !== id));
  }

  const isFull = images.length >= MAX_IMAGES;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-4">
        {images.map((image) => (
          <div
            key={image.id}
            className="group relative aspect-square overflow-hidden rounded-xl border border-white/10"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={image.dataUrl}
              alt={image.name}
              className="h-full w-full object-cover"
            />
            <button
              type="button"
              onClick={() => removeImage(image.id)}
              className="absolute right-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-black/60 text-white opacity-0 transition-opacity group-hover:opacity-100"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}

        {!isFull && (
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className={cn(
              "flex aspect-square flex-col items-center justify-center gap-1.5 rounded-xl border-2 border-dashed border-white/15 text-slate-500 transition-colors hover:border-indigo-400/50 hover:text-indigo-300"
            )}
          >
            <ImagePlus className="h-6 w-6" />
            <span className="text-xs font-medium">Them anh</span>
          </button>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        multiple
        className="hidden"
        onChange={(event) => {
          handleFiles(event.target.files);
          event.target.value = "";
        }}
      />
      <p className="text-xs text-slate-500">
        {images.length}/{MAX_IMAGES} anh / JPG, PNG, WEBP / toi da 10MB moi anh.
        Anh nay dung lam san pham, moodboard hoac reference cho video.
      </p>
    </div>
  );
}
