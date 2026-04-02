import React, { useEffect, useState } from "react"
import { useTranslation, useAstrologyLabels } from "@i18n"
import { useHelpTickets, type HelpTicket } from "@api/help"
import { formatDate } from "@utils/formatDate"
import { Clock, CheckCircle, XCircle, MessageSquare, ArrowRight } from "lucide-react"
import { Button } from "@ui/Button"
import { SkeletonGroup } from "@ui/Skeleton/Skeleton"
import { EmptyState } from "@ui/EmptyState/EmptyState"

interface SupportTicketListProps {
  refreshTrigger?: number
}

const LIMIT = 5

export function SupportTicketList({ refreshTrigger }: SupportTicketListProps) {
  const { lang } = useAstrologyLabels()
  const { help } = useTranslation("support")
  const [tickets, setTickets] = useState<HelpTicket[]>([])
  const [offset, setOffset] = useState(0)
  const [total, setTotal] = useState(0)

  const { data, isLoading, isFetching, refetch } = useHelpTickets(LIMIT, offset)

  useEffect(() => {
    if (data) {
      if (offset === 0) {
        setTickets(data.tickets)
      } else {
        setTickets(prev => [...prev, ...data.tickets])
      }
      setTotal(data.total)
    }
  }, [data, offset])

  useEffect(() => {
    if (refreshTrigger) {
      setOffset(0)
      refetch()
    }
  }, [refreshTrigger, refetch])

  const scrollToSupport = () => {
    const element = document.getElementById("help-support-section")
    if (element) {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  if (isLoading && offset === 0) {
    return (
      <div className="ticket-list-loading">
        <SkeletonGroup count={3} height="120px" gap="16px" />
      </div>
    )
  }

  if (tickets.length === 0 && !isLoading) {
    return (
      <EmptyState
        icon={<MessageSquare size={48} />}
        title={help.tickets.title}
        description={help.tickets.emptyDescription}
      >
        <Button 
          variant="ghost" 
          onClick={scrollToSupport}
          rightIcon={<ArrowRight size={18} />}
        >
          {help.hero.primaryCta}
        </Button>
      </EmptyState>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "solved":
      case "resolved":
      case "closed":
        return <CheckCircle size={14} />
      case "canceled":
        return <XCircle size={14} />
      default:
        return <Clock size={14} />
    }
  }

  const getStatusLabel = (status: string) => {
    return (help.tickets.statuses as any)[status] || status
  }

  const handleLoadMore = () => {
    setOffset(prev => prev + LIMIT)
  }

  return (
    <div className="ticket-list">
      {tickets.map((ticket) => (
        <div key={`${ticket.ticket_id}-${ticket.created_at}`} className="ticket-item">
          <div className="ticket-item__header">
            <span className="ticket-item__subject">{ticket.subject}</span>
            <div className={`ticket-badge ticket-badge--${ticket.status}`}>
              {getStatusIcon(ticket.status)}
              <span>{getStatusLabel(ticket.status)}</span>
            </div>
          </div>
          <div className="ticket-item__meta">
            <span>{formatDate(ticket.created_at, lang)}</span>
            {ticket.category_code && (
              <span className="ticket-item__category">
                • {(help.categoryDescriptions as any)[ticket.category_code]?.split('.')[0] || ticket.category_code}
              </span>
            )}
            {ticket.resolved_at && (
              <span className="ticket-item__resolved">
                • {help.tickets.resolvedAt.replace("{date}", formatDate(ticket.resolved_at, lang))}
              </span>
            )}
          </div>
          <p className="ticket-item__description">{ticket.description}</p>
          {ticket.support_response ? (
            <div className="ticket-response">
              <span className="ticket-response__label">{help.tickets.supportResponseLabel}</span>
              <p className="ticket-response__content">{ticket.support_response}</p>
            </div>
          ) : null}
        </div>
      ))}
      
      {total > tickets.length && (
        <div className="load-more-container">
          <Button 
            variant="ghost" 
            onClick={handleLoadMore}
            loading={isFetching}
            disabled={isFetching}
          >
            {help.tickets.loadMore}
          </Button>
        </div>
      )}
    </div>
  )
}
