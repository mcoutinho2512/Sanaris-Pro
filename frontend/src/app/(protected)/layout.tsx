'use client';

import { Sidebar } from "@/components/layout/sidebar";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Verificar se está autenticado (simulado por enquanto)
    const isAuthenticated = localStorage.getItem('isAuthenticated');
    
    if (!isAuthenticated && pathname !== '/login') {
      router.push('/login');
    }
  }, [pathname, router]);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto bg-gray-50">
        {children}
      </main>
    </div>
  );
}
