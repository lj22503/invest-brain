import { LLMKeyForm } from '@/components/settings/LLMKeyForm';
import { PackConfigForm } from '@/components/settings/PackConfigForm';

export default function SettingsPage() {
  return (
    <div className="p-8 overflow-y-auto flex-1 space-y-10">
      <LLMKeyForm />
      <PackConfigForm />
    </div>
  );
}
