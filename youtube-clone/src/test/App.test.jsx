import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';

describe('YouTube Clone Components', () => {
  test('renders App component', () => {
    render(<App />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  test('renders Header component', () => {
    render(<Header />);
    expect(screen.getByText('YouTube')).toBeInTheDocument();
  });

  test('renders Sidebar component', () => {
    render(<Sidebar />);
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  test('renders MainContent component with videos', () => {
    render(<MainContent />);
    expect(screen.getByText('Learn React in 1 Hour')).toBeInTheDocument();
  });
});