"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldCheck, BarChart2, Lock, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { saveConsent, getOrCreateSessionId } from "@/lib/session";

export function ConsentScreen() {
  const [agreed, setAgreed] = useState(false);
  const router = useRouter();

  const handleSubmit = () => {
    if (!agreed) return;
    getOrCreateSessionId();
    saveConsent(true);
    router.push("/chat");
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4">
      {/* 背景の装飾円 */}
      <div className="pointer-events-none absolute -top-32 -left-32 h-96 w-96 rounded-full bg-indigo-100 opacity-50 blur-3xl" />
      <div className="pointer-events-none absolute -right-32 -bottom-32 h-96 w-96 rounded-full bg-purple-100 opacity-50 blur-3xl" />

      <div className="animate-in fade-in slide-in-from-bottom-4 relative w-full max-w-lg duration-500">
        {/* キャラクターアイコン */}
        <div className="mb-6 flex flex-col items-center gap-3">
          <div className="flex h-24 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-400 to-purple-500 shadow-xl shadow-indigo-200">
            <span className="text-5xl">🐰</span>
          </div>
          <div className="text-center">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">じょぎナビ</h1>
            <p className="mt-1 text-sm text-gray-500">新入生のための Q&A チャットボット</p>
          </div>
        </div>

        {/* メインカード */}
        <div className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-xl shadow-gray-100">
          {/* カード上部の帯 */}
          <div className="h-1.5 w-full bg-gradient-to-r from-indigo-400 to-purple-500" />

          <div className="p-6">
            <h2 className="mb-4 text-base font-semibold text-gray-800">
              ご利用の前にご確認ください
            </h2>

            <div className="space-y-3">
              <InfoRow
                icon={<BarChart2 className="h-4 w-4 text-indigo-500" />}
                label="収集する情報"
                items={["会話ログ（質問と回答）", "利用時刻・回数", "評価（👍 / 👎）"]}
              />
              <InfoRow
                icon={<ShieldCheck className="h-4 w-4 text-indigo-500" />}
                label="利用目的"
                items={["回答精度の向上", "よくある質問の分析", "新入生対応の改善"]}
              />
              <InfoRow
                icon={<Lock className="h-4 w-4 text-indigo-500" />}
                label="個人情報の取り扱い"
                items={[
                  "氏名・連絡先などの個人情報は入力しないでください",
                  "収集データはじょぎ内部のみで使用",
                  "第三者への提供は行いません",
                ]}
              />
            </div>

            {/* 同意チェックボックス */}
            <div
              className={`mt-5 flex items-start gap-3 rounded-xl border-2 p-4 transition-colors duration-200 ${
                agreed ? "border-indigo-300 bg-indigo-50" : "border-gray-200 bg-gray-50"
              }`}
            >
              <Checkbox
                id="consent"
                checked={agreed}
                onCheckedChange={(checked) => setAgreed(checked === true)}
                className="mt-0.5"
              />
              <Label
                htmlFor="consent"
                className="cursor-pointer text-sm leading-relaxed text-gray-700"
              >
                上記の内容を確認し、会話ログの収集・利用に同意します
              </Label>
            </div>

            {/* ボタン */}
            <Button
              onClick={handleSubmit}
              disabled={!agreed}
              className="mt-4 h-12 w-full gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 text-base font-semibold shadow-md shadow-indigo-200 transition-all duration-200 hover:shadow-lg hover:shadow-indigo-300 disabled:opacity-40"
              size="lg"
            >
              同意してチャットを始める
              <ChevronRight className="h-5 w-5" />
            </Button>

            <p className="mt-3 text-center text-xs text-gray-400">気軽に何度でも質問できます ✨</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoRow({
  icon,
  label,
  items,
}: {
  icon: React.ReactNode;
  label: string;
  items: string[];
}) {
  return (
    <div className="rounded-xl bg-gray-50 p-3">
      <div className="mb-1.5 flex items-center gap-1.5">
        {icon}
        <span className="text-xs font-semibold tracking-wide text-gray-600 uppercase">{label}</span>
      </div>
      <ul className="space-y-1">
        {items.map((item) => (
          <li key={item} className="flex items-start gap-1.5 text-xs text-gray-500">
            <span className="mt-0.5 text-indigo-400">•</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
