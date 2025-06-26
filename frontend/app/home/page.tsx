'use client'

import { Button } from '@/components/ui/button'
import { ProcessedEvent } from '@/features/home/activity-timeline'
import { ChatMessagesView } from '@/features/home/chat-messages-view'
import { WelcomeScreen } from '@/features/home/welcome-screen'
import type { Message } from '@langchain/langgraph-sdk'
import { useStream } from '@langchain/langgraph-sdk/react'
import { useCallback, useEffect, useRef, useState } from 'react'

export default function HomePage() {
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<ProcessedEvent[]>([])
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({})
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const hasFinalizeEventOccurredRef = useRef(false)
  const [error, setError] = useState<string | null>(null)
  const thread = useStream<{
    messages: Message[]
    initial_search_query_count: number
    max_research_loops: number
    reasoning_model: string
  }>({
    apiUrl: 'http://localhost:8123',
    assistantId: 'agent',
    messagesKey: 'messages',
    onUpdateEvent: (event: any) => {
      console.log('Received event:', event)
      let processedEvent: ProcessedEvent | null = null

      // LangGraphのストリーム形式に合わせて修正
      const eventType = Object.keys(event)[0]
      const eventData = event[eventType]

      if (eventType === 'generate_query' || event.generate_query) {
        const data = eventData || event.generate_query || event
        processedEvent = {
          id: `query-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          title: 'Generating Search Queries',
          data:
            data?.search_query?.join?.(', ') || Array.isArray(data?.search_query)
              ? data.search_query.join(', ')
              : JSON.stringify(data),
        }
      } else if (eventType === 'web_research' || event.web_research) {
        const data = eventData || event.web_research || event
        const sources = data?.sources_gathered || []
        const numSources = sources.length
        const uniqueLabels = [
          ...new Set(sources.map?.((s: any) => s.label).filter?.(Boolean) || []),
        ]
        const exampleLabels = uniqueLabels.slice(0, 3).join(', ')
        processedEvent = {
          id: `research-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          title: 'Web Research',
          data: `Gathered ${numSources} sources. Related to: ${exampleLabels || 'N/A'}.`,
        }
      } else if (eventType === 'reflection' || event.reflection) {
        processedEvent = {
          id: `reflection-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          title: 'Reflection',
          data: 'Analysing Web Research Results',
        }
      } else if (eventType === 'finalize_answer' || event.finalize_answer) {
        processedEvent = {
          id: `finalize-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          title: 'Finalizing Answer',
          data: 'Composing and presenting the final answer.',
        }
        hasFinalizeEventOccurredRef.current = true
      }
      if (processedEvent) {
        setProcessedEventsTimeline((prevEvents) => [...prevEvents, processedEvent!])
      }
    },
    onError: (error: any) => {
      setError(error.message)
    },
  })

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        '[data-radix-scroll-area-viewport]',
      )
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight
      }
    }
  }, [thread.messages])

  useEffect(() => {
    if (hasFinalizeEventOccurredRef.current && !thread.isLoading && thread.messages.length > 0) {
      const lastMessage = thread.messages[thread.messages.length - 1]
      if (lastMessage && lastMessage.type === 'ai' && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }))
      }
      hasFinalizeEventOccurredRef.current = false
    }
  }, [thread.messages, thread.isLoading, processedEventsTimeline])

  const handleSubmit = useCallback(
    (submittedInputValue: string, effort: string, model: string) => {
      if (!submittedInputValue.trim()) return
      setProcessedEventsTimeline([])
      hasFinalizeEventOccurredRef.current = false

      // convert effort to, initial_search_query_count and max_research_loops
      // low means max 1 loop and 1 query
      // medium means max 3 loops and 3 queries
      // high means max 10 loops and 5 queries
      let initial_search_query_count = 0
      let max_research_loops = 0
      switch (effort) {
        case 'low':
          initial_search_query_count = 1
          max_research_loops = 1
          break
        case 'medium':
          initial_search_query_count = 3
          max_research_loops = 3
          break
        case 'high':
          initial_search_query_count = 5
          max_research_loops = 10
          break
      }

      const newMessages: Message[] = [
        ...(thread.messages || []),
        {
          type: 'human',
          content: submittedInputValue,
          id: `human-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-${performance.now()}`,
        },
      ]
      thread.submit({
        messages: newMessages,
        initial_search_query_count: initial_search_query_count,
        max_research_loops: max_research_loops,
        reasoning_model: model,
      })
    },
    [thread],
  )

  const handleCancel = useCallback(() => {
    thread.stop()
    window.location.reload()
  }, [thread])

  return (
    <div className='flex h-screen bg-neutral-800 font-sans text-neutral-100 antialiased'>
      <main className='mx-auto h-full w-full max-w-4xl'>
        {thread.messages.length === 0 ? (
          <WelcomeScreen
            handleSubmit={handleSubmit}
            isLoading={thread.isLoading}
            onCancel={handleCancel}
          />
        ) : error ? (
          <div className='flex h-full flex-col items-center justify-center'>
            <div className='flex flex-col items-center justify-center gap-4'>
              <h1 className='text-2xl font-bold text-red-400'>Error</h1>
              <p className='text-red-400'>{JSON.stringify(error)}</p>

              <Button variant='destructive' onClick={() => window.location.reload()}>
                Retry
              </Button>
            </div>
          </div>
        ) : (
          <ChatMessagesView
            messages={thread.messages}
            isLoading={thread.isLoading}
            scrollAreaRef={scrollAreaRef}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            liveActivityEvents={processedEventsTimeline}
            historicalActivities={historicalActivities}
          />
        )}
      </main>
    </div>
  )
}
