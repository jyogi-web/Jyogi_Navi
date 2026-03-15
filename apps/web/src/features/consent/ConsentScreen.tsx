'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { saveConsent, getOrCreateSessionId } from '@/lib/session';

export function ConsentScreen() {
  const [agreed, setAgreed] = useState(false);
  const router = useRouter();

  const handleSubmit = () => {
    if (!agreed) return;
    
    // セッションIDを生成・取得
    getOrCreateSessionId();
    
    // 同意状態を保存
    saveConsent(true);
    
    // チャット画面へ遷移
    router.push('/chat');
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <Card className="w-full max-w-2xl shadow-xl">
        <CardHeader className="space-y-3">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-3xl">🐰</span>
            </div>
          </div>
          <CardTitle className="text-3xl font-bold text-center">
            じょぎナビへようこそ！
          </CardTitle>
          <CardDescription className="text-center text-base">
            新入生の皆さんの質問にお答えします
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          <div className="bg-blue-50 dark:bg-blue-950/30 rounded-lg p-6 space-y-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <span>📋</span>
              <span>ご利用にあたってのお願い</span>
            </h3>
            
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>
                じょぎナビは、AIを活用してじょぎ（サークル）に関する質問にお答えするシステムです。
              </p>
              
              <div className="space-y-2">
                <p className="font-semibold text-foreground">📊 収集する情報：</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>質問内容と回答のやりとり（会話ログ）</li>
                  <li>利用時刻と回数</li>
                  <li>評価（👍 / 👎）</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <p className="font-semibold text-foreground">🎯 利用目的：</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>回答精度の向上</li>
                  <li>よくある質問の分析</li>
                  <li>新入生対応の改善</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <p className="font-semibold text-foreground">🔒 個人情報の取り扱い：</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>自由記述には氏名・連絡先などの個人情報を含めないでください</li>
                  <li>収集したデータはじょぎ内部でのみ使用します</li>
                  <li>第三者への提供は行いません</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 border rounded-lg bg-card">
            <Checkbox
              id="consent"
              checked={agreed}
              onCheckedChange={(checked) => setAgreed(checked === true)}
              className="mt-1"
            />
            <div className="flex-1">
              <Label
                htmlFor="consent"
                className="text-sm font-medium leading-relaxed cursor-pointer"
              >
                上記の内容を確認し、会話ログの収集・利用に同意します
              </Label>
            </div>
          </div>
        </CardContent>

        <CardFooter className="flex flex-col gap-3">
          <Button
            onClick={handleSubmit}
            disabled={!agreed}
            className="w-full h-12 text-lg font-semibold"
            size="lg"
          >
            同意してチャットを始める
          </Button>
          
          <p className="text-xs text-center text-muted-foreground">
            質問は何度でも可能です。気軽に聞いてください！
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
