import { TopNav } from '@/components/nav/TopNav';
import { TryChatStub } from '@/components/try/TryChatStub';

export default function TryPage() {
  return (
    <>
      <TopNav />
      <div className="pt-[72px]">
        <TryChatStub />
      </div>
    </>
  );
}