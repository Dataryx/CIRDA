import { useEffect, useRef } from 'react';
import { getWsUrl } from '@/app/config';

export type StreamTopic = 'evidence' | 'graph' | 'decision' | 'coverage' | 'benchmark' | 'audit';

export interface StreamMessage {
  topic: StreamTopic;
  payload: unknown;
  timestamp?: string;
}

interface UseStreamOptions {
  topics: StreamTopic[];
  enabled?: boolean;
  onMessage?: (message: StreamMessage) => void;
}

export function useStream({ topics, enabled = true, onMessage }: UseStreamOptions): void {
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  useEffect(() => {
    if (!enabled || topics.length === 0) return;

    const wsUrl = `${getWsUrl()}?subscribe=${topics.join(',')}`;
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event: MessageEvent<string>) => {
      try {
        const parsed = JSON.parse(event.data) as StreamMessage;
        onMessageRef.current?.(parsed);
      } catch {
        // ignore malformed messages
      }
    };

    return () => {
      socket.close();
    };
  }, [enabled, topics]);
}
