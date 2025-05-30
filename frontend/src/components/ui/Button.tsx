// 🔘 BUTTON COMPONENT - Ultra Simple Version (NO ERRORS)
import React from 'react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

// Icons per loading
import { ArrowPathIcon } from '@heroicons/react/24/outline'

// Types
interface ButtonProps {
  children?: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void
  type?: 'button' | 'submit' | 'reset'
  className?: string
  'data-testid'?: string
}

// 🎨 VARIANT STYLES
const getVariantStyles = (variant: ButtonProps['variant'] = 'primary') => {
  const styles = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg',
    secondary: 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-200 shadow-sm',
    ghost: 'hover:bg-gray-100 text-gray-700',
    danger: 'bg-red-600 hover:bg-red-700 text-white shadow-lg',
    success: 'bg-green-600 hover:bg-green-700 text-white shadow-lg'
  }
  return styles[variant]
}

// 📏 SIZE STYLES
const getSizeStyles = (size: ButtonProps['size'] = 'md') => {
  const styles = {
    sm: 'px-3 py-1.5 text-sm h-8',
    md: 'px-4 py-2 text-sm h-10',
    lg: 'px-6 py-3 text-base h-12',
    xl: 'px-8 py-4 text-lg h-14'
  }
  return styles[size]
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  fullWidth = false,
  icon,
  iconPosition = 'left',
  onClick,
  type = 'button',
  className,
  'data-testid': testId
}) => {
  // 🎨 Classi CSS
  const buttonClasses = clsx(
    // Base styles
    'inline-flex items-center justify-center font-medium rounded-xl',
    'transition-all duration-200 relative overflow-hidden',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'select-none',
    
    // Variant e size
    getVariantStyles(variant),
    getSizeStyles(size),
    
    // Stati
    fullWidth && 'w-full',
    (loading || disabled) && 'opacity-50 cursor-not-allowed',
    
    // Custom className
    className
  )

  // 🔄 Handle click
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) {
      event.preventDefault()
      return
    }
    onClick?.(event)
  }

  // 🎯 Render icon
  const renderIcon = () => {
    if (loading) {
      return (
        <motion.div
          className={clsx('flex-shrink-0', children && (iconPosition === 'left' ? 'mr-2' : 'ml-2'))}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <ArrowPathIcon className="w-4 h-4" />
        </motion.div>
      )
    }

    if (icon) {
      return (
        <span className={clsx('flex-shrink-0', children && (iconPosition === 'left' ? 'mr-2' : 'ml-2'))}>
          {icon}
        </span>
      )
    }

    return null
  }

  return (
    <motion.button
      type={type}
      className={buttonClasses}
      onClick={handleClick}
      disabled={disabled || loading}
      data-testid={testId}
      whileHover={disabled || loading ? {} : { scale: 1.02 }}
      whileTap={disabled || loading ? {} : { scale: 0.98 }}
      transition={{ duration: 0.1 }}
    >
      {/* Icon a sinistra */}
      {iconPosition === 'left' && renderIcon()}
      
      {/* Contenuto */}
      {children && (
        <span className={loading ? 'opacity-0' : ''}>
          {children}
        </span>
      )}
      
      {/* Loading text overlay */}
      {loading && children && (
        <span className="absolute inset-0 flex items-center justify-center">
          Caricamento...
        </span>
      )}
      
      {/* Icon a destra */}
      {iconPosition === 'right' && renderIcon()}
    </motion.button>
  )
}

// 🔧 BUTTON VARIANTS predefiniti
export const PrimaryButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="primary" {...props} />
)

export const SecondaryButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="secondary" {...props} />
)

export const GhostButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="ghost" {...props} />
)

export const DangerButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="danger" {...props} />
)

export const SuccessButton: React.FC<Omit<ButtonProps, 'variant'>> = (props) => (
  <Button variant="success" {...props} />
)