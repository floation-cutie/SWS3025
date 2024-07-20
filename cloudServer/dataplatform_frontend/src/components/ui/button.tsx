// src/components/ui/Button.tsx
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'destructive';
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', ...props }) => {
  const baseStyle = 'px-4 py-2 font-medium rounded focus:outline-none';
  const variantStyle = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-green-500 text-white hover:bg-green-600',
    outline: 'bg-transparent text-blue-500 border border-blue-500 hover:bg-blue-500 hover:text-white',
    destructive: 'bg-red-500 text-white hover:bg-red-600',
  };

  const className = `${baseStyle} ${variantStyle[variant]} ${props.className || ''}`;

  return (
    <button {...props} className={className}>
      {children}
    </button>
  );
};

export default Button;
