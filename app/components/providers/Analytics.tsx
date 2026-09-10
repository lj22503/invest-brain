'use client';

import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import { track, EVT } from '@/lib/analytics';

// 路由切换时上报 page_view
export default function Analytics() {
  const pathname = usePathname();
  const first = useRef(true);

  useEffect(() => {
    void track(EVT.pageView);
    if (first.current) first.current = false;
  }, [pathname]);

  return null;
}
