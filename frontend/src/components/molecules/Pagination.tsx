import React, { useMemo } from 'react'
import './Pagination.css'

interface PaginationProps {
  currentPage: number
  totalPages: number
  totalItems?: number
  itemsPerPage?: number
  onPageChange?: (page: number) => void
  onPageSizeChange?: (size: number) => void
  maxVisible?: number
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  totalItems = 0,
  itemsPerPage = 10,
  onPageChange,
  onPageSizeChange,
  maxVisible = 5,
}) => {
  // Generate page numbers with ellipsis for large pagination
  const pageNumbers = useMemo(() => {
    const pages: (number | string)[] = []

    if (totalPages <= maxVisible) {
      // Show all pages
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Always show first page
      pages.push(1)

      // Calculate range around current page
      const startPage = Math.max(2, currentPage - Math.floor(maxVisible / 2))
      const endPage = Math.min(totalPages - 1, startPage + maxVisible - 3)

      // Add ellipsis if needed
      if (startPage > 2) {
        pages.push('...')
      }

      // Add pages
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i)
      }

      // Add ellipsis if needed
      if (endPage < totalPages - 1) {
        pages.push('...')
      }

      // Always show last page
      pages.push(totalPages)
    }

    return pages
  }, [currentPage, totalPages, maxVisible])

  const handlePageClick = (page: number | string) => {
    if (typeof page === 'number' && page !== currentPage) {
      onPageChange?.(page)
    }
  }

  const handlePrevClick = () => {
    if (currentPage > 1) {
      onPageChange?.(currentPage - 1)
    }
  }

  const handleNextClick = () => {
    if (currentPage < totalPages) {
      onPageChange?.(currentPage + 1)
    }
  }

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onPageSizeChange?.(parseInt(e.target.value, 10))
  }

  // Calculate displayed items range
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  return (
    <nav className="pagination" role="navigation" aria-label="Paginação">
      <div className="pagination__container">
        {/* Info Section */}
        {totalItems > 0 && (
          <div className="pagination__info">
            Mostrando {startItem} a {endItem} de {totalItems} itens
          </div>
        )}

        {/* Controls */}
        <div className="pagination__controls">
          {/* Page Size Selector */}
          <div className="pagination__size-selector">
            <label htmlFor="page-size" className="pagination__label">
              Itens por página:
            </label>
            <select
              id="page-size"
              className="pagination__select"
              value={itemsPerPage}
              onChange={handlePageSizeChange}
              aria-label="Itens por página"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>

          {/* Pagination Buttons */}
          <div className="pagination__buttons">
            {/* Previous Button */}
            <button
              className="pagination__nav-button pagination__nav-button--prev"
              onClick={handlePrevClick}
              disabled={currentPage === 1}
              aria-label="Página anterior"
              title="Página anterior"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="15 18 9 12 15 6" />
              </svg>
              <span>Anterior</span>
            </button>

            {/* Page Buttons */}
            <div className="pagination__page-buttons">
              {pageNumbers.map((page, index) => {
                if (page === '...') {
                  return (
                    <span key={`ellipsis-${index}`} className="pagination__ellipsis">
                      ...
                    </span>
                  )
                }

                const pageNum = page as number
                const isActive = pageNum === currentPage

                return (
                  <button
                    key={`page-${pageNum}`}
                    className={`pagination__page ${isActive ? 'pagination__page--active' : ''}`}
                    onClick={() => handlePageClick(pageNum)}
                    aria-current={isActive ? 'page' : undefined}
                    aria-label={`Página ${pageNum}`}
                  >
                    {pageNum}
                  </button>
                )
              })}
            </div>

            {/* Next Button */}
            <button
              className="pagination__nav-button pagination__nav-button--next"
              onClick={handleNextClick}
              disabled={currentPage === totalPages}
              aria-label="Próxima página"
              title="Próxima página"
            >
              <span>Próxima</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          </div>
        </div>

        {/* Page Info */}
        <div className="pagination__page-info">
          Página {currentPage} de {totalPages}
        </div>
      </div>
    </nav>
  )
}

export default Pagination
