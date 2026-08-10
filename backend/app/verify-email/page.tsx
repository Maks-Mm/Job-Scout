//backend/app/verify-email/page.tsx

import { Suspense } from 'react';
import VerifyEmailContent from './VerifyEmailContent'; // Your new client component

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div>Verifying your email...</div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}

// app/verify-email/VerifyEmailContent.tsx
'use client';

import { useSearchParams } from 'next/navigation';

export default function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  // ... rest of your component logic
  return <div>Your email verification UI</div>;
}