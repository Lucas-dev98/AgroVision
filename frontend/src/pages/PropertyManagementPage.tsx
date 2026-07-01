import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Button from '@components/atoms/Button'
import Card from '@components/atoms/Card'
import Input from '@components/atoms/Input'
import Modal from '@components/molecules/Modal'
import apiService from '@services/api'
import { Property } from '@/types'
import '../styles/PropertyManagementPage.css'

type PropertyFormState = {
  name: string
  total_area: string
  planted_area: string
  location_lat: string
  location_lng: string
  soil_type: string
}

const emptyForm: PropertyFormState = {
  name: '',
  total_area: '',
  planted_area: '',
  location_lat: '',
  location_lng: '',
  soil_type: '',
}

const PropertyManagementPage: React.FC = () => {
  const navigate = useNavigate()
  const [properties, setProperties] = useState<Property[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [editingProperty, setEditingProperty] = useState<Property | null>(null)
  const [form, setForm] = useState<PropertyFormState>(emptyForm)

  const loadProperties = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiService.getProperties()
      setProperties(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao carregar propriedades'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProperties()
  }, [])

  const totalArea = useMemo(
    () => properties.reduce((sum, property) => sum + property.total_area, 0).toFixed(1),
    [properties]
  )

  const plantedArea = useMemo(
    () => properties.reduce((sum, property) => sum + property.planted_area, 0).toFixed(1),
    [properties]
  )

  const openCreateForm = () => {
    setEditingProperty(null)
    setForm(emptyForm)
    setFormOpen(true)
  }

  const openEditForm = (property: Property) => {
    setEditingProperty(property)
    setForm({
      name: property.name,
      total_area: String(property.total_area),
      planted_area: String(property.planted_area),
      location_lat: String(property.location_lat),
      location_lng: String(property.location_lng),
      soil_type: property.soil_type,
    })
    setFormOpen(true)
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError(null)

    const payload = {
      name: form.name.trim(),
      total_area: Number(form.total_area),
      planted_area: Number(form.planted_area),
      location_lat: Number(form.location_lat),
      location_lng: Number(form.location_lng),
      soil_type: form.soil_type.trim(),
    }

    try {
      if (editingProperty) {
        await apiService.updateProperty(editingProperty.id, payload)
      } else {
        await apiService.createProperty(payload)
      }
      setFormOpen(false)
      await loadProperties()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao salvar propriedade'
      setError(message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setSaving(true)
    setError(null)
    try {
      await apiService.deleteProperty(deleteId)
      setDeleteId(null)
      await loadProperties()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao excluir propriedade'
      setError(message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="property-management-page">
      <section className="property-hero">
        <div>
          <p className="property-hero__eyebrow">Estrutura fundiária</p>
          <h2>Gestão de propriedades e talhões</h2>
          <p>
            Cadastre, edite e acompanhe fazendas e áreas produtivas com uma experiência real de CRUD.
          </p>
        </div>
        <div className="property-hero__actions">
          <Button variant="secondary" size="sm" onClick={() => navigate('/rural/propriedades')}>
            Atualizar visão
          </Button>
          <Button variant="primary" size="sm" onClick={openCreateForm}>
            Nova propriedade
          </Button>
        </div>
      </section>

      <section className="property-stats">
        <Card title="Propriedades" className="property-stat-card">
          <strong>{properties.length}</strong>
          <p>unidades cadastradas</p>
        </Card>
        <Card title="Área total" className="property-stat-card">
          <strong>{totalArea} ha</strong>
          <p>soma de todas as propriedades</p>
        </Card>
        <Card title="Área plantada" className="property-stat-card">
          <strong>{plantedArea} ha</strong>
          <p>ocupação produtiva atual</p>
        </Card>
      </section>

      {error && <div className="property-alert">{error}</div>}

      {loading ? (
        <div className="property-empty">Carregando propriedades...</div>
      ) : properties.length === 0 ? (
        <div className="property-empty">
          Nenhuma propriedade cadastrada ainda. Crie a primeira para começar.
        </div>
      ) : (
        <section className="property-grid">
          {properties.map(property => (
            <Card key={property.id} title={property.name} className="property-card">
              <div className="property-card__meta">
                <span>Área total: {property.total_area} ha</span>
                <span>Área plantada: {property.planted_area} ha</span>
                <span>Solo: {property.soil_type || 'Não informado'}</span>
                <span>Coordenadas: {property.location_lat}, {property.location_lng}</span>
              </div>
              <div className="property-card__actions">
                <Button variant="secondary" size="sm" onClick={() => openEditForm(property)}>
                  Editar
                </Button>
                <Button variant="danger" size="sm" onClick={() => setDeleteId(property.id)}>
                  Excluir
                </Button>
              </div>
            </Card>
          ))}
        </section>
      )}

      <Modal
        isOpen={formOpen}
        title={editingProperty ? 'Editar propriedade' : 'Nova propriedade'}
        onClose={() => setFormOpen(false)}
        size="large"
      >
        <form className="property-form" onSubmit={handleSubmit}>
          <Input label="Nome" value={form.name} onChange={e => setForm(prev => ({ ...prev, name: e.target.value }))} required />
          <div className="property-form__row">
            <Input label="Área total (ha)" type="number" step="0.1" value={form.total_area} onChange={e => setForm(prev => ({ ...prev, total_area: e.target.value }))} required />
            <Input label="Área plantada (ha)" type="number" step="0.1" value={form.planted_area} onChange={e => setForm(prev => ({ ...prev, planted_area: e.target.value }))} required />
          </div>
          <div className="property-form__row">
            <Input label="Latitude" type="number" step="0.00000001" value={form.location_lat} onChange={e => setForm(prev => ({ ...prev, location_lat: e.target.value }))} required />
            <Input label="Longitude" type="number" step="0.00000001" value={form.location_lng} onChange={e => setForm(prev => ({ ...prev, location_lng: e.target.value }))} required />
          </div>
          <Input label="Tipo de solo" value={form.soil_type} onChange={e => setForm(prev => ({ ...prev, soil_type: e.target.value }))} required />

          <div className="property-form__actions">
            <Button variant="secondary" size="md" type="button" onClick={() => setFormOpen(false)}>
              Cancelar
            </Button>
            <Button variant="primary" size="md" type="submit" disabled={saving}>
              {saving ? 'Salvando...' : 'Salvar'}
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={deleteId !== null}
        title="Excluir propriedade"
        onClose={() => setDeleteId(null)}
        onConfirm={handleDelete}
        variant="confirmation"
        isDanger
        size="small"
      >
        <p>Tem certeza que deseja excluir esta propriedade?</p>
      </Modal>
    </div>
  )
}

export default PropertyManagementPage