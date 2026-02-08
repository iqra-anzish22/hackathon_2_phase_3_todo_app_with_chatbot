/**
 * Protected layout for authenticated routes.
 * Checks authentication on client-side and redirects to sign-in if not authenticated.
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth-api';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Check authentication on client-side
    if (!isAuthenticated()) {
      router.push('/signin?error=auth_required');
    } else {
      setIsChecking(false);
    }
  }, [router]);

  // Show loading state while checking authentication
  if (isChecking) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
}
