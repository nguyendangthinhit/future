"use client";

import { cn } from "@/lib/utils";
import type { UploadedImage } from "@/lib/types";
import { ImagePlus, X } from "lucide-react";
import { useRef } from "react";

const MAX_IMAGES = 5;
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

export function ImageUploader({
  images,
  onChange,
}: {
  images: UploadedImage[];
  onChange: (imgs: UploadedImage[]) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    const remaining = MAX_IMAGES - images.length;
    const accepted = Array.from(files).slice(0, remaining);

    accepted.forEach((file) => {
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
            file: file,
          },
        ]);
      };
      reader.readAsDataURL(file);
    });
  };

  const remove = (id: string) => onChange(images.filter((i) => i.id !== id));
  const full = images.length >= MAX_IMAGES;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-3 sm:grid-cols-4">
        {images.map((img) => (
          <div
            key={img.id}
            className="group relative aspect-square overflow-hidden rounded-xl border border-white/10"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={img.dataUrl}
              alt={img.name}
              className="h-full w-full object-cover"
            />
            <button
              type="button"
              onClick={() => remove(img.id)}
              className="absolute right-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-black/60 text-white opacity-0 transition-opacity group-hover:opacity-100"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}

        {!full && (
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className={cn(
              "flex aspect-square flex-col items-center justify-center gap-1.5 rounded-xl border-2 border-dashed border-white/15 text-slate-500 transition-colors hover:border-indigo-400/50 hover:text-indigo-300"
            )}
          >
            <ImagePlus className="h-6 w-6" />
            <span className="text-xs font-medium">Thêm ảnh</span>
          </button>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        multiple
        className="hidden"
        onChange={(e) => {
          handleFiles(e.target.files);
          e.target.value = "";
        }}
      />
      <p className="text-xs text-slate-500">
        {images.length}/{MAX_IMAGES} ảnh · JPG/PNG/WEBP · tối đa 10MB mỗi ảnh.
        Ảnh dùng cho AutoCameo (giữ nhân vật cố định).
      </p>
    </div>
  );
}
